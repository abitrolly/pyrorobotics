%module blob
%include blob.h
%{
#include "blob.h"

typedef double (*FILTER_FUNC)(double, double, double);
const FILTER_FUNC FILTER_RED = filter_red;
const FILTER_FUNC FILTER_BLUE = filter_blue;
const FILTER_FUNC FILTER_GREEN = filter_green;
const FILTER_FUNC FILTER_HUE = filter_hue;
const FILTER_FUNC FILTER_SATURATION = filter_saturation;
const FILTER_FUNC FILTER_BRIGHTNESS = filter_brightness;
%}
typedef double (*FILTER_FUNC)(double, double, double);
const FILTER_FUNC FILTER_RED = filter_red;
const FILTER_FUNC FILTER_BLUE = filter_blue;
const FILTER_FUNC FILTER_GREEN = filter_green;
const FILTER_FUNC FILTER_HUE = filter_hue;
const FILTER_FUNC FILTER_SATURATION = filter_saturation;
const FILTER_FUNC FILTER_BRIGHTNESS = filter_brightness;
