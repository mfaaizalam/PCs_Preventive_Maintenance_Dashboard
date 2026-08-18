import client from "./client";

/**
 * DELETE /api/computers/{id}
 * Removes a PC row - e.g. a stale/duplicate entry left over from a
 * renamed or reinstalled agent (see the hostname-collision error
 * message from POST /api/agent/report).
 */
export function deleteComputer(computerId) {
  return client.delete(`/api/computers/${computerId}`).then((res) => res.data);
}