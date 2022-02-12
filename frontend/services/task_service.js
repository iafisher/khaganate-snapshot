import * as apiService from "services/api_service.js";

export async function getTask(id) {
  return await apiService.get("/api/tasks/get/" + id);
}

export async function getTasks() {
  return await apiService.get("/api/tasks/list");
}

export async function createTask(task) {
  return await apiService.post("/api/tasks/create", task);
}

export async function createComment(taskId, comment) {
  return await apiService.post("/api/db/create/task-comments", {
    task: taskId,
    text: comment.text,
  });
}

export async function markFixed(taskId) {
  return await apiService.post("/api/tasks/update/" + taskId, {
    status: "fixed",
  });
}

export async function updateTask(task) {
  return await apiService.post("/api/tasks/update/" + task.id, task);
}

export async function updateTaskDeadline(taskId, newDeadline) {
  return await apiService.post("/api/tasks/update/" + taskId, {
    deadline: newDeadline,
  });
}

export async function createTimeSlot(timeSlot) {
  return await apiService.post("/api/db/create/task-time-slots", timeSlot);
}
