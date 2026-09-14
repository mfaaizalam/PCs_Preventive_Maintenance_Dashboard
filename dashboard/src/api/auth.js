import client from "./client";

export const authApi = {
  login: (username, password) =>
    client.post("/api/auth/login", { username, password }).then((r) => r.data),

  me: () => client.get("/api/auth/me").then((r) => r.data),

  changePassword: (oldPassword, newPassword) =>
    client
      .post("/api/auth/change-password", {
        old_password: oldPassword,
        new_password: newPassword,
      })
      .then((r) => r.data),
};