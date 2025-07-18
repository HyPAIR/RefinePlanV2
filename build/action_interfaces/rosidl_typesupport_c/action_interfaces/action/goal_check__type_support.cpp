// generated from rosidl_typesupport_c/resource/idl__type_support.cpp.em
// with input from action_interfaces:action/GoalCheck.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "action_interfaces/action/detail/goal_check__struct.h"
#include "action_interfaces/action/detail/goal_check__type_support.h"
#include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/message_type_support_dispatch.h"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_c/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace action_interfaces
{

namespace action
{

namespace rosidl_typesupport_c
{

typedef struct _GoalCheck_Goal_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GoalCheck_Goal_type_support_ids_t;

static const _GoalCheck_Goal_type_support_ids_t _GoalCheck_Goal_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _GoalCheck_Goal_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GoalCheck_Goal_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GoalCheck_Goal_type_support_symbol_names_t _GoalCheck_Goal_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, action_interfaces, action, GoalCheck_Goal)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, action_interfaces, action, GoalCheck_Goal)),
  }
};

typedef struct _GoalCheck_Goal_type_support_data_t
{
  void * data[2];
} _GoalCheck_Goal_type_support_data_t;

static _GoalCheck_Goal_type_support_data_t _GoalCheck_Goal_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GoalCheck_Goal_message_typesupport_map = {
  2,
  "action_interfaces",
  &_GoalCheck_Goal_message_typesupport_ids.typesupport_identifier[0],
  &_GoalCheck_Goal_message_typesupport_symbol_names.symbol_name[0],
  &_GoalCheck_Goal_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GoalCheck_Goal_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GoalCheck_Goal_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace action

}  // namespace action_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, action_interfaces, action, GoalCheck_Goal)() {
  return &::action_interfaces::action::rosidl_typesupport_c::GoalCheck_Goal_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/message_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_c/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace action_interfaces
{

namespace action
{

namespace rosidl_typesupport_c
{

typedef struct _GoalCheck_Result_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GoalCheck_Result_type_support_ids_t;

static const _GoalCheck_Result_type_support_ids_t _GoalCheck_Result_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _GoalCheck_Result_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GoalCheck_Result_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GoalCheck_Result_type_support_symbol_names_t _GoalCheck_Result_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, action_interfaces, action, GoalCheck_Result)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, action_interfaces, action, GoalCheck_Result)),
  }
};

typedef struct _GoalCheck_Result_type_support_data_t
{
  void * data[2];
} _GoalCheck_Result_type_support_data_t;

static _GoalCheck_Result_type_support_data_t _GoalCheck_Result_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GoalCheck_Result_message_typesupport_map = {
  2,
  "action_interfaces",
  &_GoalCheck_Result_message_typesupport_ids.typesupport_identifier[0],
  &_GoalCheck_Result_message_typesupport_symbol_names.symbol_name[0],
  &_GoalCheck_Result_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GoalCheck_Result_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GoalCheck_Result_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace action

}  // namespace action_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, action_interfaces, action, GoalCheck_Result)() {
  return &::action_interfaces::action::rosidl_typesupport_c::GoalCheck_Result_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/message_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_c/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace action_interfaces
{

namespace action
{

namespace rosidl_typesupport_c
{

typedef struct _GoalCheck_Feedback_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GoalCheck_Feedback_type_support_ids_t;

static const _GoalCheck_Feedback_type_support_ids_t _GoalCheck_Feedback_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _GoalCheck_Feedback_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GoalCheck_Feedback_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GoalCheck_Feedback_type_support_symbol_names_t _GoalCheck_Feedback_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, action_interfaces, action, GoalCheck_Feedback)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, action_interfaces, action, GoalCheck_Feedback)),
  }
};

typedef struct _GoalCheck_Feedback_type_support_data_t
{
  void * data[2];
} _GoalCheck_Feedback_type_support_data_t;

static _GoalCheck_Feedback_type_support_data_t _GoalCheck_Feedback_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GoalCheck_Feedback_message_typesupport_map = {
  2,
  "action_interfaces",
  &_GoalCheck_Feedback_message_typesupport_ids.typesupport_identifier[0],
  &_GoalCheck_Feedback_message_typesupport_symbol_names.symbol_name[0],
  &_GoalCheck_Feedback_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GoalCheck_Feedback_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GoalCheck_Feedback_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace action

}  // namespace action_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, action_interfaces, action, GoalCheck_Feedback)() {
  return &::action_interfaces::action::rosidl_typesupport_c::GoalCheck_Feedback_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/message_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_c/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace action_interfaces
{

namespace action
{

namespace rosidl_typesupport_c
{

typedef struct _GoalCheck_SendGoal_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GoalCheck_SendGoal_Request_type_support_ids_t;

static const _GoalCheck_SendGoal_Request_type_support_ids_t _GoalCheck_SendGoal_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _GoalCheck_SendGoal_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GoalCheck_SendGoal_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GoalCheck_SendGoal_Request_type_support_symbol_names_t _GoalCheck_SendGoal_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, action_interfaces, action, GoalCheck_SendGoal_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, action_interfaces, action, GoalCheck_SendGoal_Request)),
  }
};

typedef struct _GoalCheck_SendGoal_Request_type_support_data_t
{
  void * data[2];
} _GoalCheck_SendGoal_Request_type_support_data_t;

static _GoalCheck_SendGoal_Request_type_support_data_t _GoalCheck_SendGoal_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GoalCheck_SendGoal_Request_message_typesupport_map = {
  2,
  "action_interfaces",
  &_GoalCheck_SendGoal_Request_message_typesupport_ids.typesupport_identifier[0],
  &_GoalCheck_SendGoal_Request_message_typesupport_symbol_names.symbol_name[0],
  &_GoalCheck_SendGoal_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GoalCheck_SendGoal_Request_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GoalCheck_SendGoal_Request_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace action

}  // namespace action_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, action_interfaces, action, GoalCheck_SendGoal_Request)() {
  return &::action_interfaces::action::rosidl_typesupport_c::GoalCheck_SendGoal_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/message_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_c/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace action_interfaces
{

namespace action
{

namespace rosidl_typesupport_c
{

typedef struct _GoalCheck_SendGoal_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GoalCheck_SendGoal_Response_type_support_ids_t;

static const _GoalCheck_SendGoal_Response_type_support_ids_t _GoalCheck_SendGoal_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _GoalCheck_SendGoal_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GoalCheck_SendGoal_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GoalCheck_SendGoal_Response_type_support_symbol_names_t _GoalCheck_SendGoal_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, action_interfaces, action, GoalCheck_SendGoal_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, action_interfaces, action, GoalCheck_SendGoal_Response)),
  }
};

typedef struct _GoalCheck_SendGoal_Response_type_support_data_t
{
  void * data[2];
} _GoalCheck_SendGoal_Response_type_support_data_t;

static _GoalCheck_SendGoal_Response_type_support_data_t _GoalCheck_SendGoal_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GoalCheck_SendGoal_Response_message_typesupport_map = {
  2,
  "action_interfaces",
  &_GoalCheck_SendGoal_Response_message_typesupport_ids.typesupport_identifier[0],
  &_GoalCheck_SendGoal_Response_message_typesupport_symbol_names.symbol_name[0],
  &_GoalCheck_SendGoal_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GoalCheck_SendGoal_Response_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GoalCheck_SendGoal_Response_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace action

}  // namespace action_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, action_interfaces, action, GoalCheck_SendGoal_Response)() {
  return &::action_interfaces::action::rosidl_typesupport_c::GoalCheck_SendGoal_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/service_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace action_interfaces
{

namespace action
{

namespace rosidl_typesupport_c
{

typedef struct _GoalCheck_SendGoal_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GoalCheck_SendGoal_type_support_ids_t;

static const _GoalCheck_SendGoal_type_support_ids_t _GoalCheck_SendGoal_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _GoalCheck_SendGoal_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GoalCheck_SendGoal_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GoalCheck_SendGoal_type_support_symbol_names_t _GoalCheck_SendGoal_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, action_interfaces, action, GoalCheck_SendGoal)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, action_interfaces, action, GoalCheck_SendGoal)),
  }
};

typedef struct _GoalCheck_SendGoal_type_support_data_t
{
  void * data[2];
} _GoalCheck_SendGoal_type_support_data_t;

static _GoalCheck_SendGoal_type_support_data_t _GoalCheck_SendGoal_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GoalCheck_SendGoal_service_typesupport_map = {
  2,
  "action_interfaces",
  &_GoalCheck_SendGoal_service_typesupport_ids.typesupport_identifier[0],
  &_GoalCheck_SendGoal_service_typesupport_symbol_names.symbol_name[0],
  &_GoalCheck_SendGoal_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t GoalCheck_SendGoal_service_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GoalCheck_SendGoal_service_typesupport_map),
  rosidl_typesupport_c__get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace action

}  // namespace action_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_c, action_interfaces, action, GoalCheck_SendGoal)() {
  return &::action_interfaces::action::rosidl_typesupport_c::GoalCheck_SendGoal_service_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/message_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_c/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace action_interfaces
{

namespace action
{

namespace rosidl_typesupport_c
{

typedef struct _GoalCheck_GetResult_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GoalCheck_GetResult_Request_type_support_ids_t;

static const _GoalCheck_GetResult_Request_type_support_ids_t _GoalCheck_GetResult_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _GoalCheck_GetResult_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GoalCheck_GetResult_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GoalCheck_GetResult_Request_type_support_symbol_names_t _GoalCheck_GetResult_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, action_interfaces, action, GoalCheck_GetResult_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, action_interfaces, action, GoalCheck_GetResult_Request)),
  }
};

typedef struct _GoalCheck_GetResult_Request_type_support_data_t
{
  void * data[2];
} _GoalCheck_GetResult_Request_type_support_data_t;

static _GoalCheck_GetResult_Request_type_support_data_t _GoalCheck_GetResult_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GoalCheck_GetResult_Request_message_typesupport_map = {
  2,
  "action_interfaces",
  &_GoalCheck_GetResult_Request_message_typesupport_ids.typesupport_identifier[0],
  &_GoalCheck_GetResult_Request_message_typesupport_symbol_names.symbol_name[0],
  &_GoalCheck_GetResult_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GoalCheck_GetResult_Request_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GoalCheck_GetResult_Request_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace action

}  // namespace action_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, action_interfaces, action, GoalCheck_GetResult_Request)() {
  return &::action_interfaces::action::rosidl_typesupport_c::GoalCheck_GetResult_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/message_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_c/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace action_interfaces
{

namespace action
{

namespace rosidl_typesupport_c
{

typedef struct _GoalCheck_GetResult_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GoalCheck_GetResult_Response_type_support_ids_t;

static const _GoalCheck_GetResult_Response_type_support_ids_t _GoalCheck_GetResult_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _GoalCheck_GetResult_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GoalCheck_GetResult_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GoalCheck_GetResult_Response_type_support_symbol_names_t _GoalCheck_GetResult_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, action_interfaces, action, GoalCheck_GetResult_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, action_interfaces, action, GoalCheck_GetResult_Response)),
  }
};

typedef struct _GoalCheck_GetResult_Response_type_support_data_t
{
  void * data[2];
} _GoalCheck_GetResult_Response_type_support_data_t;

static _GoalCheck_GetResult_Response_type_support_data_t _GoalCheck_GetResult_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GoalCheck_GetResult_Response_message_typesupport_map = {
  2,
  "action_interfaces",
  &_GoalCheck_GetResult_Response_message_typesupport_ids.typesupport_identifier[0],
  &_GoalCheck_GetResult_Response_message_typesupport_symbol_names.symbol_name[0],
  &_GoalCheck_GetResult_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GoalCheck_GetResult_Response_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GoalCheck_GetResult_Response_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace action

}  // namespace action_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, action_interfaces, action, GoalCheck_GetResult_Response)() {
  return &::action_interfaces::action::rosidl_typesupport_c::GoalCheck_GetResult_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/service_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace action_interfaces
{

namespace action
{

namespace rosidl_typesupport_c
{

typedef struct _GoalCheck_GetResult_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GoalCheck_GetResult_type_support_ids_t;

static const _GoalCheck_GetResult_type_support_ids_t _GoalCheck_GetResult_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _GoalCheck_GetResult_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GoalCheck_GetResult_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GoalCheck_GetResult_type_support_symbol_names_t _GoalCheck_GetResult_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, action_interfaces, action, GoalCheck_GetResult)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, action_interfaces, action, GoalCheck_GetResult)),
  }
};

typedef struct _GoalCheck_GetResult_type_support_data_t
{
  void * data[2];
} _GoalCheck_GetResult_type_support_data_t;

static _GoalCheck_GetResult_type_support_data_t _GoalCheck_GetResult_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GoalCheck_GetResult_service_typesupport_map = {
  2,
  "action_interfaces",
  &_GoalCheck_GetResult_service_typesupport_ids.typesupport_identifier[0],
  &_GoalCheck_GetResult_service_typesupport_symbol_names.symbol_name[0],
  &_GoalCheck_GetResult_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t GoalCheck_GetResult_service_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GoalCheck_GetResult_service_typesupport_map),
  rosidl_typesupport_c__get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace action

}  // namespace action_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_c, action_interfaces, action, GoalCheck_GetResult)() {
  return &::action_interfaces::action::rosidl_typesupport_c::GoalCheck_GetResult_service_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__struct.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/message_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_c/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace action_interfaces
{

namespace action
{

namespace rosidl_typesupport_c
{

typedef struct _GoalCheck_FeedbackMessage_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GoalCheck_FeedbackMessage_type_support_ids_t;

static const _GoalCheck_FeedbackMessage_type_support_ids_t _GoalCheck_FeedbackMessage_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _GoalCheck_FeedbackMessage_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GoalCheck_FeedbackMessage_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GoalCheck_FeedbackMessage_type_support_symbol_names_t _GoalCheck_FeedbackMessage_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, action_interfaces, action, GoalCheck_FeedbackMessage)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, action_interfaces, action, GoalCheck_FeedbackMessage)),
  }
};

typedef struct _GoalCheck_FeedbackMessage_type_support_data_t
{
  void * data[2];
} _GoalCheck_FeedbackMessage_type_support_data_t;

static _GoalCheck_FeedbackMessage_type_support_data_t _GoalCheck_FeedbackMessage_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GoalCheck_FeedbackMessage_message_typesupport_map = {
  2,
  "action_interfaces",
  &_GoalCheck_FeedbackMessage_message_typesupport_ids.typesupport_identifier[0],
  &_GoalCheck_FeedbackMessage_message_typesupport_symbol_names.symbol_name[0],
  &_GoalCheck_FeedbackMessage_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GoalCheck_FeedbackMessage_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GoalCheck_FeedbackMessage_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace action

}  // namespace action_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, action_interfaces, action, GoalCheck_FeedbackMessage)() {
  return &::action_interfaces::action::rosidl_typesupport_c::GoalCheck_FeedbackMessage_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

#include "action_msgs/msg/goal_status_array.h"
#include "action_msgs/srv/cancel_goal.h"
#include "action_interfaces/action/goal_check.h"
// already included above
// #include "action_interfaces/action/detail/goal_check__type_support.h"

static rosidl_action_type_support_t _action_interfaces__action__GoalCheck__typesupport_c;

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_action_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__ACTION_SYMBOL_NAME(
  rosidl_typesupport_c, action_interfaces, action, GoalCheck)()
{
  // Thread-safe by always writing the same values to the static struct
  _action_interfaces__action__GoalCheck__typesupport_c.goal_service_type_support =
    ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(
    rosidl_typesupport_c, action_interfaces, action, GoalCheck_SendGoal)();
  _action_interfaces__action__GoalCheck__typesupport_c.result_service_type_support =
    ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(
    rosidl_typesupport_c, action_interfaces, action, GoalCheck_GetResult)();
  _action_interfaces__action__GoalCheck__typesupport_c.cancel_service_type_support =
    ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(
    rosidl_typesupport_c, action_msgs, srv, CancelGoal)();
  _action_interfaces__action__GoalCheck__typesupport_c.feedback_message_type_support =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
    rosidl_typesupport_c, action_interfaces, action, GoalCheck_FeedbackMessage)();
  _action_interfaces__action__GoalCheck__typesupport_c.status_message_type_support =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
    rosidl_typesupport_c, action_msgs, msg, GoalStatusArray)();

  return &_action_interfaces__action__GoalCheck__typesupport_c;
}

#ifdef __cplusplus
}
#endif
