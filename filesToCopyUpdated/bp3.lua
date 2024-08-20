
local BP3 = {}
BP3.__index = BP3

-- BP3.a0 = 0.010
-- BP3.amax = 0.025
-- BP3.H = 15.0
-- BP3.h = 3.0
-- BP3.rho0 = 2.670
BP3.cs = 3.464
BP3.nu = 0.25
BP3.b = 0.015
BP3.V0 = 1.0e-6
BP3.f0 = 0.6
BP3.a0 = 0.010
BP3.amax = 0.025
--BP3.H0 = 2.0
--BP3.H = 8.0
--BP3.h = 8.0

function BP3.new(params)
    local self = setmetatable({}, BP3)
    self.dipInDeg=params.dip
    self.dip = params.dip * math.pi / 180.0
    self.Vp = params.Vp
    self.inelastic=params.inelastic
    self.ratioWidthX=params.ratioWidthX
    self.widthY=params.widthY
    self.amp=params.amp
    self.depthVarying=params.depthVarying
    self.H0=params.H0
    self.H=params.H
    self.h=params.h
    --self.a0=params.a0
    --self.b=params.b

    return self
end

function BP3:boundary(x, y, t)
    local Vh = self.Vp * t
    local dist = x + y / math.tan(self.dip)
    if dist > 1 then
        Vh = -Vh / 2.0
    elseif dist < -1 then
        Vh = Vh / 2.0
    end
    return Vh * math.cos(self.dip), -Vh * math.sin(self.dip)
end

function BP3:mu(x, y)

    return self:calculateShearVelocity(x,y)^2 * self:calculateDensity(x,y)

end

function BP3:ComputeRatio(x,y)
    local r=1
    -- local withIn=self:isPointInUpperPlate(x,y)
    -- local withIn=True
    --if withIn then
    local y0=self.H+self.h/2
    local x0=y0/math.tan(self.dip)
    local widthX=self.h*self.ratioWidthX
    local widthY=self.widthY

    r=self:rotatedGaussian(x,y,self.amp,x0,-1*y0,widthX,widthY,self.dipInDeg)
    r=1-r
    --end
    if self.inelastic then
      return r
    else
      return 1

    end
end

function BP3:lam(x, y)

    return 2 * self.nu * self:mu(x,y) / (1 - 2 * self.nu)

end

function BP3:eta(x, y)

    return self:calculateShearVelocity(x,y) * self:calculateDensity(x,y) / 2.0

end

function BP3:L(x, y)
    return 0.008
end

function BP3:Sinit(x, y)
    return 0.0
end

function BP3:Vinit(x, y)
    return self.Vp
end

-- function BP3:a(x, y)
--    local d = math.abs(y) / math.sin(self.dip)
--    if d < self.H then
--        return self.a0
--    elseif d < self.H + self.h then
--        return self.a0 + (self.amax - self.a0) * (d - self.H) / self.h
--    else
--        return self.amax
--    end
-- end

function BP3:a(x, y)
    local d = math.abs(y)
    if d < self.H0 then
        return self.a0 + (self.amax - self.a0) * (self.H0 - d) / self.H0
    elseif d < self.H then
        return self.a0
    elseif d < self.H + self.h then
        return self.a0 + (self.amax - self.a0) * (d - self.H) / self.h
    else
        return self.amax
    end
end

function BP3:sn_pre(x, y)
    -- positive in compression
    -- return 50.0

    local depth=-1*y
    -- Polynomial coefficients
    local a = -1.11084929e-3
    local b = 5.38406276e-2
    local c = 2.21362824

    -- Calculate density using the polynomial
    local normal = ((a*depth^3)/3 + (b*depth^2)/2 + c*depth+1)*9.81

    if self.depthVarying == false then
     local den=self:calculateDensityValue(x,y)
     local normal=den*math.abs(y)*9.81
    end



    if normal > 50 then
        return 50.0
    end

    return normal

end

function BP3:tau_pre(x, y)
    local Vi = self:Vinit(x, y)
    local sn = self:sn_pre(x, y)
    local e = math.exp((self.f0 + self.b * math.log(self.V0 / math.abs(Vi))) / self.amax)
    return -(sn * self.amax * math.asinh((Vi / (2.0 * self.V0)) * e) + self:eta(x, y) * Vi)
end

function BP3:isPointInUpperPlate(px, py)
    local ax, ay = 0, 0
    local bx, by = 100000, 0
    local cx = bx
    local cy = -1*math.tan((self.dip)) * cx

    local function cross(ax, ay, bx, by)
        return ax * by - ay * bx
    end

    local sideABtoP = cross(bx - ax, by - ay, px - ax, py - ay)
    local sideBCtoP = cross(cx - bx, cy - by, px - bx, py - by)
    local sideCAtoP = cross(ax - cx, ay - cy, px - cx, py - cy)

    if sideABtoP * cross(bx - ax, by - ay, cx - ax, cy - ay) < 0 then return false end
    if sideBCtoP * cross(cx - bx, cy - by, ax - bx, ay - by) < 0 then return false end
    if sideCAtoP * cross(ax - cx, ay - cy, bx - cx, by - cy) < 0 then return false end

    return true
end

function BP3:rotatedGaussian(x, y, A, mu_x, mu_y, sigma_x, sigma_y, theta)
    -- Convert angle from degrees to radians
    local theta_rad = math.rad(theta)

    -- Apply rotation
    local x_prime = (x - mu_x) * math.cos(theta_rad) - (y - mu_y) * math.sin(theta_rad)
    local y_prime = (x - mu_x) * math.sin(theta_rad) + (y - mu_y) * math.cos(theta_rad)

    -- Calculate the Gaussian
    local exp_part = math.exp(-0.5 * ((x_prime^2 / sigma_x^2) + (y_prime^2 / sigma_y^2)))
    local value = A * exp_part

    return value
end

function BP3:calculateDensity(x,y)

    return self:ComputeRatio(x,y)* self:calculateDensityValue(x,y)

end

function BP3:calculateShearVelocity(x,y)

    return self:ComputeRatio(x,y)* self:calculateShearVelocityValue(x,y)

end


function BP3:calculateDensityValue(x,y)
    depth=-1*y
    -- Polynomial coefficients
    local a = -1.11084929e-3
    local b = 5.38406276e-2
    local c = 2.21362824

    if self.depthVarying == false then
     depth=50
    end

    -- Calculate density using the polynomial
    local density = a*depth^2 + b*depth + c

    -- If depth is 25 km or more, return the density at 25 km for continuity
    if depth >= 25 then
      return a*25^2 + b*25 + c
    elseif depth <= 0 then
        return c
    else
      return density
    end
end


  function BP3:calculateShearVelocityValue(x,y)
    depth=-1*y
    -- Updated cubic polynomial coefficients for shear velocity
    local a = 3.46500459e-04
    local b = -1.94746134e-02
    local c = 3.78220492e-01
    local d = 1.18604467e+00

    if self.depthVarying == false then
     depth=50
    end

    -- Ensure continuity below 0 km
    if depth <= 0 then
      return  d
    -- Ensure continuity above 25 km
    elseif depth >= 25 then
      return a * 25^3 + b * 25^2 + c * 25 + d
    else
      -- Calculate shear velocity using the updated cubic polynomial
      return a * depth^3 + b * depth^2 + c * depth + d
    end
  end
