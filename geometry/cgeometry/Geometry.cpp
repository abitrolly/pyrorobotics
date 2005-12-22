#include "Geometry.h"

Geometry::Geometry() {
}

Segment::Segment(int x1, int y1, int x2, int y2, int id) {
  this->x1 = x1;
  this->y1 = y1;
  this->x2 = x2;
  this->y2 = y2;
  this->id = id;
}

double Segment::length() {
  return sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2));
}

bool Segment::in_bbox(int x, int y){
}

bool Segment::parallel() {
}

bool Segment::vertical(Segment other) {
}

bool Segment::intersection(Segment other) {
}

PyObject *Segment::intersects(Segment other) {
  if (other.parallel()) {
    // they can "intersect" if they are collinear and overlap
    if not (in_bbox(other.x1, other.y1) || in_bbox(other.x2, other.y2)) {
      return Py_BuildValue("");
    } else if (vertical(other)) {
      if (x1 == other.x1) {
	return intersection(other);
      } else {
	return Py_BuildValue("");
      } else {
	if (yintercept() == other.yintercept()) {
	  return intersection(other);
	} else {
	  return Py_BuildValue("");
	}
      }
    }
  } else {
    i = intersection(other);
    if (in_bbox(i.x1, i.y1) and other.in_bbox(i)) {
      return i;
    } else {
      return Py_BuildValue("");
    }
  }
}

double Segment::yintercept() {
}
