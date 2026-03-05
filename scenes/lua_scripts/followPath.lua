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
                sim.wait(sim.getSimulationTimeStep()) -- advance simulation properly
                dt = sim.getSimulationTime() - st
            end
            local finalConfig = sim.getPathInterpolatedConfig(pathPts, times, times[#times])
            local threshold =0.01
            local curr_err = l2_norm_diff(getConfig(params.joints),finalConfig)
            print("current error: ",curr_err)
            while curr_err > threshold do
                -- Finish at last config
                
                for i = 1, #params.joints do
                    sim.setJointTargetPosition(params.joints[i], finalConfig[i])
                end
                curr_err = l2_norm_diff(getConfig(params.joints),finalConfig)
                print("current error: ",curr_err)
                sim.wait(0.1)
            end
            sim.wait(0.1)

            -- Clear signals to mark done
            sim.clearStringSignal(pathSignalName)
            sim.clearStringSignal(timeSignalName)
            sim.setStringSignal('FollowPathDone', '1')
        end

        sim.switchThread() -- yield to let sim continue
    end
end

function getConfig(joints)
    local c = {}
    for i=1,#joints do
        c[i] = sim.getJointPosition(joints[i])
    end
    return c
end

function l2_norm_diff(a, b)
    local s = 0.0
    for i = 1, #a do
        local d = a[i] - b[i]
        s = s + d*d
    end
    return math.sqrt(s)
end


function validateTrajectory(pathPts)
    local dof = #joints
    local steps = #pathPts / dof

    local saved = {}
    for i=1,dof do
        saved[i] = sim.getJointPosition(joints[i])
    end

    local collision = false

    for s=1,steps do
        local base = (s-1)*dof

        for j=1,dof do
            sim.setJointPosition(joints[j], pathPts[base+j])
        end

        sim.step()

        if sim.checkCollision(robotCollection,sim.handle_all) ~= 0 then
            collision = true
            break
        end
    end

    -- restore
    for i=1,dof do
        sim.setJointPosition(joints[i], saved[i])
    end

    return not collision
end