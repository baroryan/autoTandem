
local BP3 = {}
BP3.__index = BP3
BP3.rho0 = 2.670
BP3.cs = 3.464
BP3.nu = 0.25
BP3.b = 0.015
BP3.V0 = 1.0e-6
BP3.f0 = 0.6
BP3.a0 = 0.010
BP3.amax = 0.025


function BP3.new(params)
    local self = setmetatable({}, BP3)
    self.dipInDeg=params.dip
    self.dip = params.dip * math.pi / 180.0
    self.Vp = params.Vp
    self.H0=params.H0
    self.H=params.H
    self.h=params.h
    self.Dc=params.Dc
    self.rigidity=params.rigidity
    self.normalStress=params.normalStress


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

    return self.rigidity

end



function BP3:lam(x, y)

    return self.rigidity

end

function BP3:eta(x, y)

    return self.cs * self.rho0 / 2.0

end

function BP3:L(x, y)
    return self.Dc
end

function BP3:Sinit(x, y)
    return 0.0
end

function BP3:Vinit(x, y)
    return self.Vp
end



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

    return self.normalStress

end

function BP3:tau_pre(x, y)
    local Vi = self:Vinit(x, y)
    local sn = self:sn_pre(x, y)
    local e = math.exp((self.f0 + self.b * math.log(self.V0 / math.abs(Vi))) / self.amax)
    return -(sn * self.amax * math.asinh((Vi / (2.0 * self.V0)) * e) + self:eta(x, y) * Vi)
end
