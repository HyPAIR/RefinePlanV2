-- threaded customization script: FollowPathThreaded.lua

sim = require('sim')
simIK = require('simIK')
simOMPL = require('simOMPL')

-- GLOBAL PARAMS
params = {}

function sysCall_thread()
    -- Robot joints
    params.joints = {}
    for i = 1, 6 do
        params.joints[i] = sim.getObject('/UR10/joint'..i)
    end
    params.robotTip = sim.getObject('/UR10/tip')
    params.robotTarget = sim.getObject('/UR10/target')
    params.robotBase = sim.getObject('/UR10')

    -- FK limits (example)
    local fkVel, fkAccel, fkJerk = 180, 40, 80
    params.fkMaxVel = {fkVel*math.pi/180,fkVel*math.pi/180,fkVel*math.pi/180,fkVel*math.pi/180,fkVel*math.pi/180,fkVel*math.pi/180}
    params.fkMaxAccel = {fkAccel*math.pi/180,fkAccel*math.pi/180,fkAccel*math.pi/180,fkAccel*math.pi/180,fkAccel*math.pi/180,fkAccel*math.pi/180}

    -- Signal to receive path from Python
    local pathSignalName = 'FollowPathSignal'
    local timeSignalName = 'FollowPathTimes'
    local moveToPoseSignalName ='moveToPose'

    sim.setStepping(true)

    while true do
        -- Check if a new path has been sent from Python
        local pathData = sim.getStringSignal(pathSignalName)
        local timeData = sim.getStringSignal(timeSignalName)
        if pathData and timeData then
            -- Convert strings back to tables
            local pathPts = sim.unpackTable(pathData)
            local times = sim.unpackTable(timeData)

            local st = sim.getSimulationTime()
            local dt = 0

            while dt < times[#times] do
                local config = sim.getPathInterpolatedConfig(pathPts, times, dt)
                for i = 1, #params.joints do
                    sim.setJointTargetPosition(params.joints[i], config[i])
                end
                sim.wait(0.01) -- advance simulation properly
                dt = sim.getSimulationTime() - st
            end

            -- Finish at last config
            local finalConfig = sim.getPathInterpolatedConfig(pathPts, times, times[#times])
            for i = 1, #params.joints do
                sim.setJointTargetPosition(params.joints[i], finalConfig[i])
            end
            sim.wait(1.0)
            local configTable={
            joints =params.joints,
            targetPos = finalConfig,
            --vel =params.fkVel,
            --maxVel = params.fkMaxvel,
            --accel = params.fkAccel,
            --maxAccel = params.fkMaxAccel
            }
            
            --sim.moveToConfig(configTable)
            sim.step()
            sim.setStepping(false)

            -- Clear signals to mark done
            sim.clearStringSignal(pathSignalName)
            sim.clearStringSignal(timeSignalName)
            sim.setStringSignal('FollowPathDone', '1')
        end

        sim.switchThread() -- yield to let sim continue
    end
end

