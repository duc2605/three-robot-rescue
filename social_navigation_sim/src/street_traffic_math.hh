#pragma once
#include <algorithm>
#include <array>
#include <cmath>
namespace rescue { namespace street {
struct V {
  double x{},y{};
  V operator+(V b)const{return {x+b.x,y+b.y};}
  V operator-(V b)const{return {x-b.x,y-b.y};}
  V operator*(double k)const{return {x*k,y*k};}
};
inline double dot(V a,V b){return a.x*b.x+a.y*b.y;}
inline double norm(V v){return std::hypot(v.x,v.y);}
inline double angle(double a){return std::atan2(std::sin(a),std::cos(a));}
inline double sweptGap(V a,V b,V p,V q){
  V d=a-p,v=(b-a)-(q-p);double t=std::clamp(-dot(d,v)/std::max(1e-12,dot(v,v)),0.,1.);
  return norm(d+v*t);
}
inline bool inJunction(V p){return std::abs(p.x)<9.8&&std::abs(p.y)<9.8;}
inline int crosswalkAxis(V p){
  if(std::abs(std::abs(p.x)-8.)<=.9&&std::abs(p.y)<6.35)return 1;
  if(std::abs(std::abs(p.y)-8.)<=.9&&std::abs(p.x)<6.35)return 0;
  return -1;
}
inline bool onCrosswalk(V p){return crosswalkAxis(p)>=0;}
inline double stopCenter(double lineCenter,double front,double halfLine=.07,double gap=.15){
  return lineCenter-front-halfLine-gap;
}
struct Phase {int approach;bool green,yellow,pedestrian;double remaining;};
inline Phase phase(double seconds){
  double t=std::fmod(std::max(0.,seconds),128.);
  if(t>=80.)return {-1,false,false,true,128.-t};
  int a=int(t/20.);double local=t-20.*a;
  return {a,local<14.,local>=14.&&local<17.,false,20.-local};
}
// Phase.approach identifies the timing slot. Opposite approaches share lights.
inline bool servesApproach(Phase phase,int approach){
  return !phase.pedestrian&&approach>=0&&approach<4
      &&phase.approach%2==approach%2;
}
struct Signals {
  bool vehicleGreen{},vehicleYellow{};
  std::array<bool,2> pedestrianGreen{{false,false}};
  std::array<double,2> pedestrianRemaining{{0.,0.}};
};
inline Signals signalState(Phase phase,bool foreignCar,bool carsInCrossing,
                           std::array<bool,2> occupiedCrossings){
  Signals result;
  if(phase.pedestrian){
    result.pedestrianGreen={{!carsInCrossing,!carsInCrossing}};
    result.pedestrianRemaining={{phase.remaining,phase.remaining}};
    return result;
  }
  int axis=phase.approach%2;
  bool blocked=foreignCar||occupiedCrossings[1-axis];
  result.vehicleGreen=phase.green&&!blocked;
  result.vehicleYellow=phase.yellow&&!blocked;
  result.pedestrianGreen[axis]=result.vehicleGreen;
  if(result.vehicleGreen)result.pedestrianRemaining[axis]=std::max(0.,phase.remaining-6.);
  return result;
}
}}
