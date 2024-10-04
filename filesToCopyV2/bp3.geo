DefineConstant[ Lf = {0.020, Min 0, Max 10, Name "Fault resolution" } ];
DefineConstant[ Ls = {0.020, Min 0, Max 10, Name "Resolution near free surface" } ];
DefineConstant[ dip = {10, Min 0, Max 90, Name "Dipping angle" } ];
DefineConstant[ vwMaxDepth = {15, Min 0, Max 400, Name "vwMaxDepth" } ];
DefineConstant[ vwMinDepth = {2, Min 0, Max 400, Name "vwMinDepth" } ];
DefineConstant[ depthfaultEnds = {18, Min 0, Max 400, Name "depthfaultEnds" } ];
DefineConstant[ meshSizeWithDistance = {0.5, Min 0, Max 10, Name "meshSizeWithDistance" } ];

Printf("Value of vwMinDepth: %g", vwMinDepth);
Printf("Value of vwMaxDepth: %g", vwMaxDepth);
Printf("Value of depthfaultEnds: %g", depthfaultEnds);

// Check the first condition: vwMinDepth < vwMaxDepth
If (vwMinDepth < vwMaxDepth)
    // Check the second condition: vwMaxDepth < depthfaultEnds
    If (vwMaxDepth < depthfaultEnds)
        // Both conditions are true, print the message
        Printf("Conditions are met: vwMinDepth (%g) < vwMaxDepth (%g) < depthfaultEnds (%g)", vwMinDepth, vwMaxDepth, depthfaultEnds);
        // Continue with the script...
    Else
        // Second condition failed
        Printf("Error: vwMaxDepth (%g) should be less than depthfaultEnds (%g)", vwMaxDepth, depthfaultEnds);
        // Exit the script
        Exit;
    EndIf
Else
    // First condition failed
    Printf("Error: vwMinDepth (%g) should be less than vwMaxDepth (%g)", vwMinDepth, vwMaxDepth);
    // Exit the script
    Exit;
EndIf

dip_rad = dip * Pi / 180.0;

h = 40;
d = 400;
/*d = 180;*/
w = d * Cos(dip_rad) / Sin(dip_rad);
w = w < d ? d : w;
d1 = 100;
d2 = 120;
d3 = 140;
d4 = 160;
Point(1) = {-w, 0, 0, h};
Point(2) = {w, 0, 0, h};
Point(3) = {w + d * Cos(dip_rad) / Sin(dip_rad), -d, 0, h};
Point(4) = {-w + d * Cos(dip_rad) / Sin(dip_rad), -d, 0, h};
Point(5) = {d * Cos(dip_rad) / Sin(dip_rad), -d, 0, h};
Point(6) = {0, 0, 0, h};


Point(11) = {vwMinDepth / Tan(dip_rad), -vwMinDepth, 0, h};
Point(12) = {vwMaxDepth / Tan(dip_rad), -vwMaxDepth, 0, h};
Point(13) = {depthfaultEnds / Tan(dip_rad), -depthfaultEnds, 0, h};

Line(1) = {1, 6};
Line(2) = {6, 2};
Line(3) = {2, 3};
Line(4) = {3, 5};
Line(5) = {5, 4};
Line(6) = {4, 1};


Line(12) = {6, 11};
Line(13) = {11, 12}; //vm fault with high res
Line(14) = {12, 13};
Line(15) = {13, 5};

Curve Loop(1) = {12,13,14,15, -4, -3, -2};
Curve Loop(2) = {12,13,14,15, 5, 6, 1};
Plane Surface(1) = {1};
Plane Surface(2) = {2};
/* Bottom: Free-surface */
Physical Curve(3) = {12,13,14};
Physical Curve(1) = {1, 2, 4, 5};
Physical Curve(5) = {3, 6, 15};

Physical Surface(1) = {1};
Physical Surface(2) = {2};

Field[1] = Distance;
Field[1].CurvesList = {13}; // Distance from high resolution fault line
Field[1].NumPointsPerCurve = 100000;

Field[2] = MathEval;
Field[2].F = Sprintf("%g + %g * F1", Lf,meshSizeWithDistance); // Distance field from high resolution fault line


Field[3] = MathEval;
Field[3].F = Sprintf("%g + 0.1 * sqrt(x^2 + y^2)", Ls);
Field[4] = Min;
Field[4].FieldsList = {2, 3};

Background Field = 4;
Mesh.MshFileVersion = 2.2;
