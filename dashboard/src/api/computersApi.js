import client from "./client";

/**
 * PATCH /api/computers/{id}
 * Edits department / lab name / asset ID from the dashboard's pencil
 * icons. Send only the field(s) that changed - omitted fields are
 * left alone server-side.
 */
export function updateComputer(computerId, updates) {
  return client.patch(`/api/computers/${computerId}`, updates).then((res) => res.data);
}

/**
 * DELETE /api/computers/{id}
 * Removes a PC row - e.g. a stale/duplicate entry left over from a
 * renamed or reinstalled agent (see the hostname-collision error
 * message from POST /api/agent/report).
 */
export function deleteComputer(computerId) {
  return client.delete(`/api/computers/${computerId}`).then((res) => res.data);
}