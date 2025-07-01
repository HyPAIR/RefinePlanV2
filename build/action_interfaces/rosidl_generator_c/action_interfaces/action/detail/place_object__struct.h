// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from action_interfaces:action/PlaceObject.idl
// generated code does not contain a copyright notice

#ifndef ACTION_INTERFACES__ACTION__DETAIL__PLACE_OBJECT__STRUCT_H_
#define ACTION_INTERFACES__ACTION__DETAIL__PLACE_OBJECT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'pose'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in action/PlaceObject in the package action_interfaces.
typedef struct action_interfaces__action__PlaceObject_Goal
{
  rosidl_runtime_c__float__Sequence pose;
} action_interfaces__action__PlaceObject_Goal;

// Struct for a sequence of action_interfaces__action__PlaceObject_Goal.
typedef struct action_interfaces__action__PlaceObject_Goal__Sequence
{
  action_interfaces__action__PlaceObject_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} action_interfaces__action__PlaceObject_Goal__Sequence;


// Constants defined in the message

/// Struct defined in action/PlaceObject in the package action_interfaces.
typedef struct action_interfaces__action__PlaceObject_Result
{
  bool success;
} action_interfaces__action__PlaceObject_Result;

// Struct for a sequence of action_interfaces__action__PlaceObject_Result.
typedef struct action_interfaces__action__PlaceObject_Result__Sequence
{
  action_interfaces__action__PlaceObject_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} action_interfaces__action__PlaceObject_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'currentpose'
// already included above
// #include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in action/PlaceObject in the package action_interfaces.
typedef struct action_interfaces__action__PlaceObject_Feedback
{
  rosidl_runtime_c__float__Sequence currentpose;
} action_interfaces__action__PlaceObject_Feedback;

// Struct for a sequence of action_interfaces__action__PlaceObject_Feedback.
typedef struct action_interfaces__action__PlaceObject_Feedback__Sequence
{
  action_interfaces__action__PlaceObject_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} action_interfaces__action__PlaceObject_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "action_interfaces/action/detail/place_object__struct.h"

/// Struct defined in action/PlaceObject in the package action_interfaces.
typedef struct action_interfaces__action__PlaceObject_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  action_interfaces__action__PlaceObject_Goal goal;
} action_interfaces__action__PlaceObject_SendGoal_Request;

// Struct for a sequence of action_interfaces__action__PlaceObject_SendGoal_Request.
typedef struct action_interfaces__action__PlaceObject_SendGoal_Request__Sequence
{
  action_interfaces__action__PlaceObject_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} action_interfaces__action__PlaceObject_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/PlaceObject in the package action_interfaces.
typedef struct action_interfaces__action__PlaceObject_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} action_interfaces__action__PlaceObject_SendGoal_Response;

// Struct for a sequence of action_interfaces__action__PlaceObject_SendGoal_Response.
typedef struct action_interfaces__action__PlaceObject_SendGoal_Response__Sequence
{
  action_interfaces__action__PlaceObject_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} action_interfaces__action__PlaceObject_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/PlaceObject in the package action_interfaces.
typedef struct action_interfaces__action__PlaceObject_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} action_interfaces__action__PlaceObject_GetResult_Request;

// Struct for a sequence of action_interfaces__action__PlaceObject_GetResult_Request.
typedef struct action_interfaces__action__PlaceObject_GetResult_Request__Sequence
{
  action_interfaces__action__PlaceObject_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} action_interfaces__action__PlaceObject_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "action_interfaces/action/detail/place_object__struct.h"

/// Struct defined in action/PlaceObject in the package action_interfaces.
typedef struct action_interfaces__action__PlaceObject_GetResult_Response
{
  int8_t status;
  action_interfaces__action__PlaceObject_Result result;
} action_interfaces__action__PlaceObject_GetResult_Response;

// Struct for a sequence of action_interfaces__action__PlaceObject_GetResult_Response.
typedef struct action_interfaces__action__PlaceObject_GetResult_Response__Sequence
{
  action_interfaces__action__PlaceObject_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} action_interfaces__action__PlaceObject_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "action_interfaces/action/detail/place_object__struct.h"

/// Struct defined in action/PlaceObject in the package action_interfaces.
typedef struct action_interfaces__action__PlaceObject_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  action_interfaces__action__PlaceObject_Feedback feedback;
} action_interfaces__action__PlaceObject_FeedbackMessage;

// Struct for a sequence of action_interfaces__action__PlaceObject_FeedbackMessage.
typedef struct action_interfaces__action__PlaceObject_FeedbackMessage__Sequence
{
  action_interfaces__action__PlaceObject_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} action_interfaces__action__PlaceObject_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ACTION_INTERFACES__ACTION__DETAIL__PLACE_OBJECT__STRUCT_H_
