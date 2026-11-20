"""Contact material defaults. Explicit body properties override preset values."""
import math
PRESETS={
 'jelly':dict(mass=1.,stiffness=95.,damping=2.9,recovery_amplitude=.22,recovery_frequency=3.2,recovery_damping=.24),
 'jelly_soft':dict(mass=1.,stiffness=60.,damping=2.6,recovery_amplitude=.30,recovery_frequency=2.3,recovery_damping=.22),
 'jelly_firm':dict(mass=1.,stiffness=175.,damping=5.5,recovery_amplitude=.12,recovery_frequency=4.4,recovery_damping=.42),
 'rubber':dict(mass=1.,stiffness=260.,damping=4.5,recovery_amplitude=.09,recovery_frequency=5.6,recovery_damping=.48),
 'silicone':dict(mass=1.,stiffness=140.,damping=11.,recovery_amplitude=.07,recovery_frequency=3.1,recovery_damping=.78),
 'foam':dict(mass=.65,stiffness=105.,damping=12.,recovery_amplitude=.04,recovery_frequency=2.5,recovery_damping=.85),
 'heavy':dict(mass=2.5,stiffness=260.,damping=19.,recovery_amplitude=.08,recovery_frequency=1.8,recovery_damping=.66),
}
def resolve(body):
 p=body.get('preset')
 if p is not None and p not in PRESETS:raise ValueError(f'unknown contact preset {p}; choose {list(PRESETS)}')
 b={**PRESETS.get(p,{}),**body}
 a,f,d=[float(b.get(k,v)) for k,v in [('recovery_amplitude',0),('recovery_frequency',3.2),('recovery_damping',.3)]]
 if not (0<=a<=.4 and .3<=f<=12 and .08<=d<=.98):raise ValueError('invalid recovery settings')
 return b

def recovery(elapsed,amplitude,frequency,damping):
 if elapsed<0:return 0.
 w=2*math.pi*frequency;wd=w*math.sqrt(1-damping*damping)
 return amplitude*math.exp(-damping*w*elapsed)*math.sin(wd*elapsed)
