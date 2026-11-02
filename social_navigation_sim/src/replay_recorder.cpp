// Evaluation only: read ECM model/actor poses; never publish navigation inputs.
#include <chrono>
#include <cstdlib>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <string>
#include <map>
#include <sstream>
#include <vector>
#include <algorithm>
#include <ignition/gazebo/components/Collision.hh>
#include <ignition/gazebo/components/ContactSensorData.hh>
#include <ignition/common/Console.hh>
#include <ignition/gazebo/System.hh>
#include <ignition/gazebo/Util.hh>
#include <ignition/gazebo/components/Actor.hh>
#include <ignition/gazebo/components/Model.hh>
#include <ignition/gazebo/components/Name.hh>
#include <ignition/gazebo/components/ParentEntity.hh>
#include <ignition/plugin/Register.hh>

namespace rescue {
static std::string Quote(const std::string &value) {
  std::string result="\"";
  for (unsigned char c : value) {
    if (c=='"' || c=='\\') { result+='\\'; result+=c; }
    else if (c<32) result+='?';
    else result+=c;
  }
  return result+'"';
}
class ReplayRecorder : public ignition::gazebo::System,
  public ignition::gazebo::ISystemConfigure, public ignition::gazebo::ISystemPreUpdate, public ignition::gazebo::ISystemPostUpdate {
  ignition::gazebo::Entity world{ignition::gazebo::kNullEntity};
  std::ofstream output;
  double previous{-1.}, recorded{-1.};
  unsigned epoch{0};
  std::chrono::steady_clock::time_point lastWall{};
  struct Hit { std::string a,b,c1,c2; double first,last,depth; unsigned steps; std::string position; };
  std::map<std::pair<uint64_t,uint64_t>, Hit> pending;
  std::string ModelName(ignition::gazebo::Entity entity,
                        const ignition::gazebo::EntityComponentManager &ecm) const {
    for (unsigned i=0;i<64 && entity!=ignition::gazebo::kNullEntity;++i) {
      auto parent=ecm.Component<ignition::gazebo::components::ParentEntity>(entity);
      if (!parent) return "";
      if (parent->Data()==world) {
        auto name=ecm.Component<ignition::gazebo::components::Name>(entity);
        return name?name->Data():"";
      }
      entity=parent->Data();
    }
    return "";
  }
  bool Robot(const std::string &name) const {
    return name=="robot1" || name=="robot2" || name=="robot3";
  }
 public:
  void PreUpdate(const ignition::gazebo::UpdateInfo &,
                 ignition::gazebo::EntityComponentManager &ecm) override {
    if (!output.is_open()) return;
    // Ask Physics for contacts on existing robot collision shapes, including
    // wheels and camera. Never add geometry or change masks / physical response.
    std::vector<ignition::gazebo::Entity> requested;
    ecm.Each<ignition::gazebo::components::Collision>(
      [&](const ignition::gazebo::Entity &e,const auto *) {
        if (Robot(ModelName(e,ecm)) &&
            !ecm.Component<ignition::gazebo::components::ContactSensorData>(e)) requested.push_back(e);
        return true;
      });
    for (auto e:requested)
      ecm.CreateComponent(e,ignition::gazebo::components::ContactSensorData());
  }
  void Configure(const ignition::gazebo::Entity &entity, const std::shared_ptr<const sdf::Element> &,
                 ignition::gazebo::EntityComponentManager &, ignition::gazebo::EventManager &) override {
    world=entity;
    const char *directory=std::getenv("SOCIAL_REPLAY_DIRECTORY");
    if (!directory || !*directory) return;
    output.open(std::string(directory)+"/world_frames.jsonl",std::ios::app);
    if (!output) { ignerr << "Replay recorder cannot open output directory\n"; return; }
    output << std::setprecision(12);
    ignmsg << "Replay recorder: measured ECM top-level model/actor poses, 20 Hz sim; evaluation only.\n";
  }
  void PostUpdate(const ignition::gazebo::UpdateInfo &info,
                  const ignition::gazebo::EntityComponentManager &ecm) override {
    if (!output.is_open() || !output.good()) return;
    const double now=std::chrono::duration<double>(info.simTime).count();
    const auto wall=std::chrono::steady_clock::now();
    if (now<previous) { ++epoch; recorded=-1.; pending.clear(); }
    previous=now;
    if (!info.paused) {
      // Collect every physics step, before the pose sampling gate, so a short
      // contact survives until the next 20 Hz output frame.
      ecm.Each<ignition::gazebo::components::Collision,ignition::gazebo::components::ContactSensorData>(
        [&](const ignition::gazebo::Entity &,const auto *,const auto *data) {
          for (const auto &contact:data->Data().contact()) {
            auto id1=contact.collision1().id(), id2=contact.collision2().id();
            auto a=ModelName(id1,ecm), b=ModelName(id2,ecm);
            if (a.empty() || b.empty() || a==b || (!Robot(a)&&!Robot(b))) continue;
            auto key=std::make_pair(std::min(id1,id2),std::max(id1,id2));
            double depth=-1.;
            for (auto d:contact.depth()) if (std::isfinite(d)) depth=std::max(depth,d);
            std::string position="null";
            if (contact.position_size()>0) {
              const auto &p=contact.position(0);
              if (std::isfinite(p.x()) && std::isfinite(p.y()) && std::isfinite(p.z())) {
                std::ostringstream point; point << std::setprecision(12)
                  << '[' << p.x() << ',' << p.y() << ',' << p.z() << ']';
                position=point.str();
              }
            }
            auto found=pending.find(key);
            if (found==pending.end())
              pending.emplace(key,Hit{a,b,ignition::gazebo::scopedName(id1,ecm,"::",false),
                ignition::gazebo::scopedName(id2,ecm,"::",false),now,now,depth,1,position});
            else {
              if (found->second.last!=now) ++found->second.steps;
              found->second.last=now;
              found->second.depth=std::max(found->second.depth,depth);
            }
          }
          return true;
        });
    }
    if (info.paused) {
      if (std::chrono::duration<double>(wall-lastWall).count()<1.) return;
    } else if (now-recorded < .05-1e-9) return;
    recorded=now; lastWall=wall;
    output << "{\"t\":" << now << ",\"epoch\":" << epoch
           << ",\"paused\":" << (info.paused?"true":"false") << ",\"objects\":[";
    bool first=true;
    auto write=[&](ignition::gazebo::Entity entity, const std::string &name, const char *kind) {
      auto parent=ecm.Component<ignition::gazebo::components::ParentEntity>(entity);
      if (!parent || parent->Data()!=world) return;
      const auto pose=ignition::gazebo::worldPose(entity,ecm);
      if (!std::isfinite(pose.X()) || !std::isfinite(pose.Y()) || !std::isfinite(pose.Z())
          || !std::isfinite(pose.Roll()) || !std::isfinite(pose.Pitch()) || !std::isfinite(pose.Yaw())) return;
      if (!first) output << ',';
      first=false;
      output << "{\"id\":" << entity << ",\"name\":" << Quote(name)
             << ",\"kind\":\"" << kind << "\",\"p\":["
             << pose.X() << ',' << pose.Y() << ',' << pose.Z() << ','
             << pose.Roll() << ',' << pose.Pitch() << ',' << pose.Yaw() << "]}";
    };
    ecm.Each<ignition::gazebo::components::Model,ignition::gazebo::components::Name>(
      [&](const ignition::gazebo::Entity &e, const auto *, const auto *name) {
        write(e,name->Data(),"model"); return true;
      });
    ecm.Each<ignition::gazebo::components::Actor,ignition::gazebo::components::Name>(
      [&](const ignition::gazebo::Entity &e, const auto *, const auto *name) {
        write(e,name->Data(),"actor"); return true;
      });
    output << "],\"physics_contact_source\":\"Gazebo ContactSensorData\",\"contacts\":[";
    first=true;
    for (const auto &item:pending) {
      const auto &hit=item.second;
      if (!first) output << ',';
      first=false;
      output << "{\"a\":" << Quote(hit.a) << ",\"b\":" << Quote(hit.b)
        << ",\"collision1\":" << Quote(hit.c1) << ",\"collision2\":" << Quote(hit.c2)
        << ",\"first_t\":" << hit.first << ",\"last_t\":" << hit.last
        << ",\"max_depth\":" << (hit.depth<0?"null":std::to_string(hit.depth))
        << ",\"position\":" << hit.position << ",\"steps\":" << hit.steps << '}';
    }
    output << "]}\n"; output.flush(); pending.clear();
  }
};
}
IGNITION_ADD_PLUGIN(rescue::ReplayRecorder,ignition::gazebo::System,
                    rescue::ReplayRecorder::ISystemConfigure,rescue::ReplayRecorder::ISystemPreUpdate,
                    rescue::ReplayRecorder::ISystemPostUpdate)
IGNITION_ADD_PLUGIN_ALIAS(rescue::ReplayRecorder,"rescue::ReplayRecorder")
