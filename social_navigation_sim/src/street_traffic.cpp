// Scenario-only traffic: ECM truth is never published to the navigation inputs.
#include "street_traffic_math.hh"
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <limits>
#include <map>
#include <memory>
#include <sstream>
#include <string>
#include <stdexcept>
#include <cstddef>
#include <vector>
#include <ignition/common/Console.hh>
#include <ignition/transport/Node.hh>
#include <ignition/msgs/stringmsg.pb.h>
#include <ignition/gazebo/System.hh>
#include <ignition/gazebo/Model.hh>
#include <ignition/gazebo/Util.hh>
#include <ignition/gazebo/components/Model.hh>
#include <ignition/gazebo/components/Name.hh>
#include <ignition/plugin/Register.hh>

namespace rescue {
using street::V;
struct StreetCar {
  std::string name;int approach{};double initial{},s{},stop{},maxSpeed{},speed{};
  std::vector<V> points;std::vector<double> distance;double yieldStop{-1};int yieldSide{};
  bool leftTurn{},yieldingOncoming{};
};
struct StreetAgent {
  std::string name,kind;V start,end,p,velocity;double speed{},radius{},yaw{},stride{},side{},walkSpeed{},runSpeed{},runAfter{},travelled{};bool running{};
  bool active{},reverse{};long lastStartWindow{-1};
};
struct StreetSignal {V p;double yaw{};int approach{},axis{};};
struct Obstacle {std::string name;V p,v;double radius;};
class StreetTraffic:public ignition::gazebo::System,
 public ignition::gazebo::ISystemConfigure,public ignition::gazebo::ISystemPreUpdate {
  std::vector<StreetCar> cars;
  std::vector<StreetAgent> agents;
  std::map<std::string,ignition::gazebo::Entity> entities;
  std::vector<StreetSignal> signals,pedestrianSignals;
  ignition::transport::Node transport;
  ignition::transport::Node::Publisher statePublisher;
  double lastState{-1};
  double previous{-1},lastLog{-1},phaseDelay{};
  std::ofstream log;
  static V Read(const std::string &text){V p;std::istringstream s(text);s>>p.x>>p.y;return p;}
  std::pair<V,double> At(const StreetCar &c,double distance)const {
    distance=std::clamp(distance,0.,c.distance.back());
    auto upper=std::upper_bound(c.distance.begin(),c.distance.end(),distance);
    size_t i=std::min(c.points.size()-2,size_t(std::max<std::ptrdiff_t>(0,upper-c.distance.begin()-1)));
    V d=c.points[i+1]-c.points[i];double f=(distance-c.distance[i])/std::max(1e-9,street::norm(d));
    return {c.points[i]+d*f,std::atan2(d.y,d.x)};
  }
  bool Set(const std::string &name,const ignition::math::Pose3d &p,ignition::gazebo::EntityComponentManager &ecm){
    auto i=entities.find(name);if(i==entities.end())return false;
    ignition::gazebo::Model(i->second).SetWorldPoseCmd(ecm,p);return true;
  }
  void Pose(const std::string &name,V p,double yaw,ignition::gazebo::EntityComponentManager &ecm,double z=0){
    Set(name,{p.x,p.y,z,0,0,yaw},ecm);
  }
  void Reset(){
    for(auto &c:cars){c.s=c.initial;c.speed=0.;c.yieldingOncoming=false;}
    for(auto &a:agents){a.p=a.start;a.velocity={};a.active=false;a.reverse=false;
      a.lastStartWindow=-1;a.travelled=0;a.running=false;a.speed=a.walkSpeed;a.yaw=std::atan2(a.end.y-a.start.y,a.end.x-a.start.x);a.stride=0;a.side=0;}
  }
  bool AgentSpace(const StreetAgent &a,V p)const{
    // Keep a walker in its crossing corridor (including lateral passing space).
    V d=a.end-a.start;double length=street::norm(d);d=d*(1./length);V n{-d.y,d.x};
    double longitudinal=street::dot(p-a.start,d);
    return longitudinal>=-.12&&longitudinal<=length+.12 && std::abs(street::dot(p-a.start,n))<=1.15;
  }
  void Animate(StreetAgent &a,double dt,ignition::gazebo::EntityComponentManager &ecm){
    double speed=street::norm(a.velocity);
    a.stride+=speed*dt*((a.kind=="runner"||a.running)?8.:a.kind=="dog"?10.:7.);
    double amplitude=speed<.03?0.:((a.kind=="runner"||a.running)?.65:.35);
    for(int i=0;i<4;i++){
      double pitch=amplitude*std::sin(a.stride+(i%2?3.14159265359:0)+(i>=2?3.14159265359:0));
      double lx=0,ly=(i%2?-.13:.13),z=.48;
      if(a.kind=="dog"){lx=i<2?.23:-.23;ly=(i%2?-.12:.12);z=.22;}
      else if(i>=2){ly=(i%2?-.25:.25);z=1.02;}
      lx+=.10*std::sin(pitch);
      double c=std::cos(a.yaw),s=std::sin(a.yaw);
      ignition::math::Quaterniond rotation(0,pitch,a.yaw);
      Set(a.name+"_limb_"+std::to_string(i),
          ignition::math::Pose3d({a.p.x+c*lx-s*ly,a.p.y+s*lx+c*ly,z},rotation),ecm);
    }
  }
 public:
  void Configure(const ignition::gazebo::Entity &,const std::shared_ptr<const sdf::Element> &sdf,
    ignition::gazebo::EntityComponentManager &,ignition::gazebo::EventManager &)override {
    auto cfg=sdf->Clone();
    for(auto e=cfg->GetElement("vehicle");e;e=e->GetNextElement("vehicle")){
      StreetCar c;c.name=e->Get<std::string>("name");c.approach=e->Get<int>("approach");
      c.initial=e->Get<double>("initial_s");c.stop=std::min(e->Get<double>("stop_s"),street::stopCenter(26.,1.33));c.maxSpeed=e->Get<double>("speed");
      for(auto p=e->GetElement("point");p;p=p->GetNextElement("point"))c.points.push_back(Read(p->Get<std::string>()));
      c.distance.push_back(0.);for(size_t i=1;i<c.points.size();i++)c.distance.push_back(c.distance.back()+street::norm(c.points[i]-c.points[i-1]));
      if(c.points.size()<2 || c.maxSpeed<=0 || c.approach<0 || c.approach>3)throw std::runtime_error("Invalid street car");
      double turn=street::angle(At(c,c.distance.back()).second-At(c,0.).second);
      c.leftTurn=turn>.5;
      // A turning car yields before the parallel pedestrian exit crossing.
      for(double distance=c.stop;distance<c.distance.back();distance+=.1){
        V point=At(c,distance).first;
        if(street::crosswalkAxis(point)==c.approach%2){
          c.yieldStop=std::max(c.stop,distance-1.33-.15);
          c.yieldSide=(c.approach%2==0?point.y:point.x)>0?1:0;
          break;
        }
      }
      cars.push_back(c);
    }
    for(auto e=cfg->GetElement("agent");e;e=e->GetNextElement("agent")){
      StreetAgent a;a.name=e->Get<std::string>("name");a.kind=e->Get<std::string>("kind");
      a.start=Read(e->Get<std::string>("start"));a.end=Read(e->Get<std::string>("end"));
      a.speed=e->Get<double>("speed");a.radius=e->Get<double>("radius");
      if(a.speed<=0||a.radius<=0||street::norm(a.end-a.start)<1)throw std::runtime_error("Invalid street agent");
      a.walkSpeed=a.speed;
      a.runAfter=e->HasElement("run_after_distance")?e->Get<double>("run_after_distance"):0.;
      a.runSpeed=e->HasElement("running_speed")?e->Get<double>("running_speed"):a.speed;
      agents.push_back(a);
    }
    for(auto e=cfg->GetElement("signal");e;e=e->GetNextElement("signal")){
      int approach=e->Get<int>("approach");
      signals.push_back({Read(e->Get<std::string>("xy")),e->Get<double>("yaw"),approach});
    }
    if(cfg->HasElement("pedestrian_signal"))
      for(auto e=cfg->GetElement("pedestrian_signal");e;e=e->GetNextElement("pedestrian_signal"))
        pedestrianSignals.push_back({Read(e->Get<std::string>("xy")),e->Get<double>("yaw"),0,e->Get<int>("axis")});
    statePublisher=transport.Advertise<ignition::msgs::StringMsg>("/street/traffic_state");
    if(signals.size()!=4)throw std::runtime_error("Street needs four signal heads");
    if(const char* directory=std::getenv("SOCIAL_REPLAY_DIRECTORY")){
      log.open(std::string(directory)+"/traffic.jsonl");log<<std::setprecision(12);
    }
    Reset();ignmsg<<"Street intersection: "<<cars.size()<<" vehicles, "<<agents.size()<<" walkers/runners/cane/animal.\n";
  }
  void PreUpdate(const ignition::gazebo::UpdateInfo &info,ignition::gazebo::EntityComponentManager &ecm)override{
    if(info.paused)return;
    double now=std::chrono::duration<double>(info.simTime).count();
    if(now<previous){Reset();previous=-1;lastLog=lastState=-1;phaseDelay=0;}
    if(previous>=0&&now-previous<.05)return;
    double dt=previous<0?.05:std::min(.1,now-previous);previous=now;
    if(entities.empty())ecm.Each<ignition::gazebo::components::Model,ignition::gazebo::components::Name>(
      [&](const auto &e,const auto*,const auto*n){entities[n->Data()]=e;return true;});
    // Robots spawn later: update only missing named robots, not every scene entity.
    for(const auto &n:{"robot1","robot2","robot3"})if(!entities.count(n)){
      auto e=ecm.EntityByComponents(ignition::gazebo::components::Model(),ignition::gazebo::components::Name(n));
      if(e!=ignition::gazebo::kNullEntity)entities[n]=e;
    }
    auto phase=street::phase(now-phaseDelay);long cycle=long((now-phaseDelay)/128.);
    std::vector<Obstacle> obstacles;
    bool carsInCrossing=false,foreignCar=false,robotsCrossing=false;
    std::array<bool,2> occupiedCrossings{{false,false}};
    std::array<std::array<bool,2>,2> crossingUsers{};
    for(const auto &c:cars){auto p=At(c,c.s);
      obstacles.push_back({c.name,p.first,{std::cos(p.second)*c.speed,std::sin(p.second)*c.speed},1.5});
      if(street::inJunction(p.first)){
        carsInCrossing=true;if(!street::servesApproach(phase,c.approach))foreignCar=true;
      }
    }
    for(const auto &a:agents){
      obstacles.push_back({a.name,a.p,a.velocity,a.radius});
      int axis=std::abs(a.end.x-a.start.x)>std::abs(a.end.y-a.start.y)?0:1;
      if(a.active)occupiedCrossings[axis]=true;
    }
    for(const auto &n:{"robot1","robot2","robot3"}){
      auto it=entities.find(n);if(it!=entities.end()){
        auto p=ignition::gazebo::worldPose(it->second,ecm);
        obstacles.push_back({n,{p.X(),p.Y()},{},.20});
        int axis=street::crosswalkAxis({p.X(),p.Y()});
        if(axis>=0){
          robotsCrossing=true;occupiedCrossings[axis]=true;
          crossingUsers[axis][(axis==0?p.Y():p.X())>0?1:0]=true;
        }
      }
    }
    // Hold the phase at its boundary until the conflicting users clear.
    // Conflicting directions remain red until the previous crossing is clear.
    double boundary=cycle*128.+(phase.pedestrian?80.:phase.approach*20.);
    bool clearanceWait=(phase.pedestrian&&carsInCrossing)
        ||(phase.green&&(occupiedCrossings[1-phase.approach%2]||foreignCar));
    if(clearanceWait){
      phaseDelay+=std::max(0.,now-phaseDelay-boundary);
      phase=street::phase(now-phaseDelay);
    }
    const auto lights=street::signalState(phase,foreignCar,carsInCrossing,occupiedCrossings);
    bool green=lights.vehicleGreen;
    bool walk=lights.pedestrianGreen[0]||lights.pedestrianGreen[1];
    long permissionWindow=cycle*5+(phase.pedestrian?4:phase.approach);
    for(auto &a:agents){
      V target=a.reverse?a.start:a.end;
      int axis=std::abs(a.end.x-a.start.x)>std::abs(a.end.y-a.start.y)?0:1;
      if(!a.active && lights.pedestrianGreen[axis] && permissionWindow>a.lastStartWindow
          && lights.pedestrianRemaining[axis]>.5){
        a.active=true;a.travelled=0;a.running=false;a.speed=a.walkSpeed;
        a.lastStartWindow=permissionWindow;
      }
      if(a.active && a.runAfter>0 && a.travelled>=a.runAfter){a.running=true;a.speed=a.runSpeed;}
      V selected{};double best=-1e9;int selectedSide=0;
      if(a.active){
        V to=target-a.p;double distance=street::norm(to);
        if(distance<.18){a.active=false;a.reverse=!a.reverse;}
        else{
          double direct=std::atan2(to.y,to.x);
          if(street::norm(a.velocity)<.05 && std::abs(street::angle(direct-a.yaw))>1.){
            // Turn at the kerb before the return crossing, without stepping
            // outside the endpoint corridor or walking backwards.
            a.yaw+=std::clamp(street::angle(direct-a.yaw),-2.8*dt,2.8*dt);
          }else{
          for(double offset:{0.,.30,-.30,.55,-.55,.80,-.80}){
            const double desiredYaw=direct+offset;
            V candidate{},sim=a.p;double simYaw=a.yaw,clearance=100.;bool safe=true;
            // Predict the turning arc, not a straight extrapolation of the first
            // small steering step. This permits early smooth left/right passing.
            for(int k=0;k<16&&safe;k++){
              double step=k==0?dt:.1;
              simYaw+=std::clamp(street::angle(desiredYaw-simYaw),-2.8*step,2.8*step);
              double remaining=street::norm(target-sim);
              if(k>0&&remaining<.18)break;
              double speed=std::min({a.speed,remaining/std::max(.001,step),street::norm(a.velocity)+.9*(k==0?dt:dt+k*.1)});
              V velocity{std::cos(simYaw)*speed,std::sin(simYaw)*speed};
              if(k==0)candidate=velocity;
              V next=sim+velocity*step;
              if(!AgentSpace(a,next)){safe=false;break;}
              double t0=k==0?0.:dt+(k-1)*.1,t1=t0+step;
              for(const auto &o:obstacles){if(o.name==a.name)continue;
                V before=o.p+o.v*t0,after=o.p+o.v*t1;
                double current=street::norm(sim-before);
                double future=street::sweptGap(sim,next,before,after);
                double required=a.radius+o.radius+.13;
                if(future<required && !(current<required && street::norm(next-after)>current+.001)){
                  safe=false;break;
                }
                clearance=std::min(clearance,future-required);
              }
              sim=next;
            }
            if(!safe)continue;
            int side=offset>.01?1:offset<-.01?-1:0;
            double score=street::dot(candidate,to*(1./distance))+.20*std::min(clearance,1.)-.08*std::abs(offset);
            if(a.side!=0&&side==int(a.side))score+=.08;
            if(score>best){best=score;selected=candidate;selectedSide=side;}
          }
          if(street::norm(selected)>.01){a.p=a.p+selected*dt;a.travelled+=street::norm(selected)*dt;a.yaw=std::atan2(selected.y,selected.x);a.side=selectedSide;}
          }
        }
      }
      a.velocity=selected;
      Pose(a.name,a.p,a.yaw,ecm);Animate(a,dt,ecm);
    }
    for(const auto &a:agents)if(a.active){
      int axis=std::abs(a.end.x-a.start.x)>std::abs(a.end.y-a.start.y)?0:1;
      crossingUsers[axis][(axis==0?a.start.y:a.start.x)>0?1:0]=true;
    }
    for(auto &c:cars){
      bool passed=c.s>c.stop+.02;
      bool permit=passed||(green&&street::servesApproach(phase,c.approach));
      // Yield before entering the junction to the head of the opposing queue.
      // A car queued behind another left turn does not take precedence over it.
      const StreetCar *oncoming=nullptr;
      for(const auto &other:cars){
        if(other.approach!=(c.approach+2)%4)continue;
        if(other.s>other.stop+.02&&!street::inJunction(At(other,other.s).first))continue;
        if(oncoming==nullptr||other.s>oncoming->s)oncoming=&other;
      }
      c.yieldingOncoming=c.leftTurn&&c.s<=c.stop+.02&&oncoming!=nullptr
          &&!oncoming->leftTurn&&(street::inJunction(At(*oncoming,oncoming->s).first)
              ||(green&&oncoming->stop-oncoming->s<=oncoming->maxSpeed*6.));
      if(c.yieldingOncoming)permit=false;
      double limit=c.maxSpeed;
      if(!permit)limit=std::min(limit,std::sqrt(std::max(0.,2*.9*(c.stop-c.s))));
      auto p=At(c,c.s);
      // Same-approach queue headway and yield to an occupied crossing/robot.
      for(const auto &o:obstacles){if(o.name==c.name)continue;
        V d=o.p-p.first;double ahead=d.x*std::cos(p.second)+d.y*std::sin(p.second);
        double lateral=std::abs(-d.x*std::sin(p.second)+d.y*std::cos(p.second));
        if(ahead>0&&lateral<.8+o.radius){
          double gap=ahead-1.4-o.radius-.65;
          limit=std::min(limit,std::sqrt(std::max(0.,2*.9*gap)));
        }
      }
      bool yieldPedestrians=c.yieldStop>=0&&c.s<=c.yieldStop+.02
          &&crossingUsers[c.approach%2][c.yieldSide];
      if(yieldPedestrians)limit=std::min(limit,std::sqrt(std::max(0.,2*.9*(c.yieldStop-c.s))));
      c.speed=std::clamp(limit,std::max(0.,c.speed-1.4*dt),c.speed+.65*dt);
      double advance=c.speed*dt;
      if(!permit)advance=std::min(advance,std::max(0.,c.stop-c.s));
      if(yieldPedestrians)advance=std::min(advance,std::max(0.,c.yieldStop-c.s));
      auto q=At(c,c.s+advance);
      bool collision=false;
      for(const auto &o:obstacles)if(o.name!=c.name){
        double initial=street::norm(p.first-o.p);
        double minimum=street::sweptGap(p.first,q.first,o.p,o.p+o.v*dt);
        if(minimum<1.5+o.radius+.15 && minimum<initial-1e-5){collision=true;break;}
      }
      if(!collision){c.s+=advance;c.speed=advance/dt;}else c.speed=0.;
      if(c.s>=c.distance.back()-.05){
        bool free=true;auto spawn=At(c,0.).first;
        for(const auto &o:obstacles)if(o.name!=c.name&&street::norm(spawn-o.p)<4.)free=false;
        if(free){c.s=0.;c.speed=0.;} // Respawn only beyond visible ends, never in intersection.
      }
      p=At(c,c.s);Pose(c.name,p.first,p.second,ecm);
    }
    for(size_t i=0;i<signals.size();i++){
      const auto &head=signals[i];
      bool g=green&&street::servesApproach(phase,head.approach);
      bool y=lights.vehicleYellow&&street::servesApproach(phase,head.approach);
      Pose("signal_"+std::to_string(i)+"_red",head.p,head.yaw,ecm,g||y?-10:3.3);
      Pose("signal_"+std::to_string(i)+"_yellow",head.p,head.yaw,ecm,y?3.0:-10);
      Pose("signal_"+std::to_string(i)+"_green",head.p,head.yaw,ecm,g?2.7:-10);
    }
    for(size_t i=0;i<pedestrianSignals.size();i++){
      const auto &head=pedestrianSignals[i];
      Pose("pedestrian_"+std::to_string(i)+"_walk",head.p,head.yaw,ecm,lights.pedestrianGreen[head.axis]?2.0:-10);
      Pose("pedestrian_"+std::to_string(i)+"_wait",head.p,head.yaw,ecm,lights.pedestrianGreen[head.axis]?-10:2.43);
    }
    if(now-lastState>=.2){
      lastState=now;
      std::ostringstream state;
      state<<"{\"version\":1,\"stamp\":"<<std::setprecision(12)<<now
           <<",\"pedestrian_green\":"<<(walk?"true":"false")
           <<",\"cars_in_crossing\":"<<(carsInCrossing?"true":"false")
           <<",\"robots_crossing\":"<<(robotsCrossing?"true":"false")
           <<",\"pedestrian_green_axes\":["<<(lights.pedestrianGreen[0]?"true":"false")<<","<<(lights.pedestrianGreen[1]?"true":"false")<<"]"
           <<",\"pedestrian_remaining_axes\":["<<lights.pedestrianRemaining[0]<<","<<lights.pedestrianRemaining[1]<<"]"
           <<",\"phase_time\":"<<(now-phaseDelay)<<",\"phase_remaining\":"<<phase.remaining
           <<",\"approach\":"<<phase.approach<<",\"vehicle_green\":"<<(green?"true":"false")
           <<",\"vehicle_green_approaches\":[";
      for(int approach=0;approach<4;approach++){
        if(approach)state<<',';
        state<<(green&&street::servesApproach(phase,approach)?"true":"false");
      }
      state<<"]}";
      ignition::msgs::StringMsg message;message.set_data(state.str());statePublisher.Publish(message);
    }
    if(log&&now-lastLog>=.2){
      lastLog=now;log<<"{\"t\":"<<now<<",\"cycle\":"<<cycle<<",\"approach\":"<<phase.approach
        <<",\"green\":"<<(green?"true":"false")<<",\"pedestrian_green\":"<<(walk?"true":"false")
           <<",\"pedestrian_green_axes\":["<<(lights.pedestrianGreen[0]?"true":"false")<<","<<(lights.pedestrianGreen[1]?"true":"false")<<"]"
        <<",\"cars_in_crossing\":"<<(carsInCrossing?"true":"false")
        <<",\"robots_crossing\":"<<(robotsCrossing?"true":"false")
        <<",\"vehicle_green_approaches\":[";
      for(int approach=0;approach<4;approach++){
        if(approach)log<<',';
        log<<(green&&street::servesApproach(phase,approach)?"true":"false");
      }
      log<<"],\"agents\":[";
      bool first=true;for(const auto &a:agents){if(!first)log<<',';first=false;
        log<<"{\"name\":\""<<a.name<<"\",\"p\":["<<a.p.x<<','<<a.p.y<<"],\"v\":["<<a.velocity.x<<','<<a.velocity.y
           <<"],\"running\":"<<(a.running||a.kind=="runner"?"true":"false")<<",\"passing_side\":"<<a.side<<",\"active\":"<<(a.active?"true":"false")<<'}';}
      log<<"],\"cars\":[";first=true;
      for(const auto &car:cars){
        if(!first)log<<',';first=false;auto point=At(car,car.s).first;
        log<<"{\"name\":\""<<car.name<<"\",\"p\":["<<point.x<<','<<point.y
           <<"],\"speed\":"<<car.speed<<",\"route_s\":"<<car.s
           <<",\"stop_s\":"<<car.stop<<",\"approach_stop_gap\":"<<(26.-.07-car.s-1.33)
           <<",\"yield_stop_s\":"<<car.yieldStop
           <<",\"yielding_oncoming\":"<<(car.yieldingOncoming?"true":"false")<<"}";
      }
      log<<"]}\n";log.flush();
    }
  }
};
}
IGNITION_ADD_PLUGIN(rescue::StreetTraffic,ignition::gazebo::System,
  ignition::gazebo::ISystemConfigure,ignition::gazebo::ISystemPreUpdate)
IGNITION_ADD_PLUGIN_ALIAS(rescue::StreetTraffic,"rescue::StreetTraffic")
