function sysCall_init()
    sim = require'sim'
    simROS2 = require'simROS2'
end

function actsrv_handle_goal(goal_id,goal)
    sim.addLog(sim.verbosity_msgs,string.format('actsrv_handle_goal: goal_id=%s, goal=%s',goal_id,table.tostring(goal)))
    if current_goal then
        return simROS2.goal_response.reject
    end
    if goal.order > 9000 then
        return simROS2.goal_response.reject
    else
        return simROS2.goal_response.accept_and_execute
    end
end

function actsrv_handle_cancel(goal_id,goal)
    sim.addLog(sim.verbosity_msgs,string.format('actsrv_handle_cancel: goal_id=%s, goal=%s',goal_id,table.tostring(goal)))
    if current_goal and current_goal.id==goal_id then
        current_goal=nil
    end
    return simROS2.cancel_response.accept
end

function actsrv_handle_accepted(goal_id,goal)
    sim.addLog(sim.verbosity_msgs,string.format('actsrv_handle_accepted: goal_id=%s, goal=%s',goal_id,table.tostring(goal)))
    current_goal={
        id=goal_id,
        order=goal.order,
        status={0, 1},
        mtime=sim.getSystemTime()
    }
end

function sysCall_thread()
    current_goal=nil
    sim.addLog(sim.verbosity_msgs,'thread started')
    actsrv=simROS2.createActionServer('/fibonacci','example_interfaces/action/Fibonacci', actsrv_handle_goal, actsrv_handle_cancel, actsrv_handle_accepted)
    while true do
        if current_goal and current_goal.mtime+1<sim.getSystemTime() then
            -- make one step every second
            current_goal.mtime=sim.getSystemTime()
            
            if simROS2.actionServerActionIsCanceling(actsrv,current_goal.id) then
                local result=simROS2.createInterface('example_interfaces/action/FibonacciResult')
                result.sequence=current_goal.status
                simROS2.actionServerActionCanceled(actsrv,current_goal.id,result)
                sim.addLog(sim.verbosity_msgs,string.format('canceled goal %s',current_goal.id))
            else
                local n=#current_goal.status
                current_goal.status[n+1]=current_goal.status[n]+current_goal.status[n-1]
                local feedback=simROS2.createInterface('example_interfaces/action/FibonacciFeedback')
                feedback.sequence=current_goal.status
                simROS2.actionServerPublishFeedback(actsrv,current_goal.id,feedback)
                sim.addLog(sim.verbosity_msgs,string.format('goal %s feedback',current_goal.id))
                
                if n==current_goal.order then
                    local result=simROS2.createInterface('example_interfaces/action/FibonacciResult')
                    result.sequence=current_goal.status
                    simROS2.actionServerActionSucceed(actsrv,current_goal.id,result)
                    sim.addLog(sim.verbosity_msgs,string.format('goal %s succeeded',current_goal.id))
                    current_goal=nil
                end
            end
        end
        sim.step()
    end
end

function sysCall_cleanup()
    simROS2.shutdownActionServer(actsrv)
    sim.addLog(sim.verbosity_msgs,'thread finished')
end
