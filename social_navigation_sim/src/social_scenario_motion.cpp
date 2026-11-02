// Scripted, simulation-time humans. Scenario poses never enter ROS perception.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <memory>
#include <string>
#include <stdexcept>
#include <vector>
#include <ignition/common/Console.hh>
#include <ignition/gazebo/System.hh>
#include <ignition/gazebo/Model.hh>
#include <ignition/gazebo/Util.hh>
#include <ignition/gazebo/components/Model.hh>
#include <ignition/gazebo/components/Name.hh>
#include <ignition/plugin/Register.hh>

namespace rescue
{
struct Keyframe { double time; ignition::math::Pose3d pose; };
struct Motion
{
  std::string name;
  double start{}, end{}, period{};
  std::vector<Keyframe> frames;
  ignition::gazebo::Entity entity{ignition::gazebo::kNullEntity};
  bool active{false};
  double activatedAt{};
  bool verified{false};
};

class SocialScenarioMotion : public ignition::gazebo::System,
  public ignition::gazebo::ISystemConfigure, public ignition::gazebo::ISystemPreUpdate
{
  std::vector<Motion> motions;
  double previous{-1.};
 public:
  void Configure(const ignition::gazebo::Entity &, const std::shared_ptr<const sdf::Element> &sdf,
                 ignition::gazebo::EntityComponentManager &, ignition::gazebo::EventManager &) override
  {
    auto config = sdf->Clone();
    for (auto entry = config->GetElement("motion"); entry; entry = entry->GetNextElement("motion"))
    {
      Motion motion;
      motion.name = entry->Get<std::string>("model");
      motion.start = entry->Get<double>("start");
      motion.end = entry->Get<double>("end");
      motion.period = entry->Get<double>("period");
      for (auto key = entry->GetElement("key"); key; key = key->GetNextElement("key"))
        motion.frames.push_back({key->Get<double>("time"), key->Get<ignition::math::Pose3d>("pose")});
      if (motion.frames.empty() || motion.period <= 0. || motion.end <= motion.start)
        throw std::runtime_error("Invalid social motion: " + motion.name);
      motions.push_back(std::move(motion));
    }
    ignmsg << "Social dynamic scenario loaded: " << motions.size()
           << " model tracks; simulation-time, kinematic collision bodies.\n";
  }

  void PreUpdate(const ignition::gazebo::UpdateInfo &info,
                 ignition::gazebo::EntityComponentManager &ecm) override
  {
    if (info.paused) return;
    const double now = std::chrono::duration<double>(info.simTime).count();
    if (now >= previous && now-previous < .05) return;
    previous = now;
    for (auto &motion : motions)
    {
      if (motion.entity == ignition::gazebo::kNullEntity)
        motion.entity = ecm.EntityByComponents(ignition::gazebo::components::Name(motion.name),
                                               ignition::gazebo::components::Model());
      if (motion.entity == ignition::gazebo::kNullEntity) continue;
      const double phase = std::fmod(std::max(0., now), motion.period);
      const bool active = phase >= motion.start && phase < motion.end;
      ignition::math::Pose3d pose(0, 0, -50, 0, 0, 0);
      if (active)
      {
        auto after = std::upper_bound(motion.frames.begin(), motion.frames.end(), phase,
          [](double t, const Keyframe &key) {return t < key.time;});
        if (after == motion.frames.begin()) pose = after->pose;
        else if (after == motion.frames.end()) pose = motion.frames.back().pose;
        else
        {
          const auto &a = *(after-1), &b = *after;
          const double alpha = (phase-a.time)/(b.time-a.time);
          const auto position = a.pose.Pos()*(1.-alpha) + b.pose.Pos()*alpha;
          const auto rotation = ignition::math::Quaterniond::Slerp(alpha, a.pose.Rot(), b.pose.Rot());
          pose = ignition::math::Pose3d(position, rotation);
        }
      }
      ignition::gazebo::Model(motion.entity).SetWorldPoseCmd(ecm, pose);
      if (active && motion.active && !motion.verified && now-motion.activatedAt > .25)
      {
        const auto actual = ignition::gazebo::worldPose(motion.entity, ecm);
        if (actual.Pos().Distance(pose.Pos()) < .1)
          ignmsg << "Social motion verified in physics: " << motion.name << " at " << actual.Pos() << "\n";
        else
          ignerr << "Social motion pose mismatch: " << motion.name << " actual " << actual.Pos()
                 << " target " << pose.Pos() << "\n";
        motion.verified = true;
      }
      if (active != motion.active)
      {
        motion.active = active;
        motion.activatedAt = now;
        motion.verified = false;
        ignmsg << "Social scenario: " << motion.name << (active ? " active" : " hidden")
               << " at simulation second " << now << "\n";
      }
    }
  }
};
}
IGNITION_ADD_PLUGIN(rescue::SocialScenarioMotion, ignition::gazebo::System,
  ignition::gazebo::ISystemConfigure, ignition::gazebo::ISystemPreUpdate)
IGNITION_ADD_PLUGIN_ALIAS(rescue::SocialScenarioMotion, "rescue::SocialScenarioMotion")
