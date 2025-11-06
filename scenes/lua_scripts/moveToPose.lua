functionfunction sysCall_init()
    sim = require('sim')

    -- Put some initialization code here
    -- sim.setStepping(true) -- enabling stepping mode
end

function sysCall_thread()
    sim = require('sim')
    sim.setThreadSwitchTiming(2)  -- allow CoppeliaSim to yield between steps

    while true do
        -- Check for a pending moveToPose signal
        local moveSignal = sim.getStringSignal('moveToPoseSignal')
        if moveSignal then
            sim.clearStringSignal('moveToPoseSignal')
            local p = sim.unpackTable(moveSignal)
            handleMoveToPose(p)
        end

        sim.switchThread() -- yield to allow stepping
    end
end
