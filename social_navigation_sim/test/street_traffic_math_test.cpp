// Standalone numerical regression, no Gazebo/ROS launched.
#include "../src/street_traffic_math.hh"
#include <cassert>
#include <cmath>
int main(){
  using namespace rescue::street;
  auto a=phase(0.);assert(a.approach==0&&a.green&&!a.pedestrian);
  a=phase(14.);assert(a.yellow&&!a.green);
  a=phase(17.);assert(!a.green&&!a.yellow&&!a.pedestrian);
  a=phase(20.);assert(a.approach==1&&a.green);
  a=phase(79.9);assert(a.approach==3&&!a.green&&!a.pedestrian);
  a=phase(80.);assert(a.pedestrian&&!a.green&&a.remaining==48.);
  a=phase(128.);assert(a.approach==0&&a.green);
  for(double seconds:{0.,14.,20.,34.,40.,60.}){
    auto paired=phase(seconds);
    for(int approach=0;approach<4;approach++)
      assert(servesApproach(paired,approach)==(approach%2==paired.approach%2));
  }
  assert(!servesApproach(phase(80.),0));
  assert(!servesApproach(phase(80.),2));
  assert(!servesApproach(phase(0.),-1));
  auto lights=signalState(phase(0.),false,false,{{false,false}});
  assert(lights.vehicleGreen&&lights.pedestrianGreen[0]&&!lights.pedestrianGreen[1]);
  lights=signalState(phase(20.),false,false,{{false,false}});
  assert(lights.vehicleGreen&&!lights.pedestrianGreen[0]&&lights.pedestrianGreen[1]);
  lights=signalState(phase(0.),false,false,{{true,false}});
  assert(lights.vehicleGreen&&lights.pedestrianGreen[0]);
  lights=signalState(phase(0.),false,false,{{false,true}});
  assert(!lights.vehicleGreen&&!lights.pedestrianGreen[0]);
  lights=signalState(phase(14.),false,false,{{false,false}});
  assert(lights.vehicleYellow&&!lights.pedestrianGreen[0]&&!lights.pedestrianGreen[1]);
  assert(std::abs(stopCenter(26.,1.33)-24.45)<1e-9);
  assert(inJunction({0,0}));
  assert(!inJunction({-10,-2.5}));
  assert(!inJunction({-2.5,35.7}));
  assert(onCrosswalk({8,0}));
  assert(!onCrosswalk({0,0}));
  assert(sweptGap({-1,0},{1,0},{0,-1},{0,1})<1e-9);
  assert(std::abs(sweptGap({0,0},{1,0},{0,1},{1,1})-1.)<1e-9);
  assert(std::abs(angle(3.14159265359*2+.1)-.1)<1e-9);
}
