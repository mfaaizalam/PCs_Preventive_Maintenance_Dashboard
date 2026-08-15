// Hardcoded login roster.
//
// This is intentionally NOT a real auth system — there's no backend
// user table wired up for login (see app/models/user.py, which
// exists but has no /api/auth routes). This just lets the ~3 people
// who actually do maintenance on these PCs pick their name so ticks
// get attributed correctly, and keeps random visitors on the network
// from ticking boxes as someone else.
//
// To change who can log in, edit this list. To wire this up to the
// real `users` table + hashed passwords instead, you'd add
// app/api/auth.py (login endpoint checking User.hashed_password) and
// swap AuthContext's login() to call it instead of checking this array.
export const USERS = [
  { id: "it-support", name: "IT Support", pin: "1111" },
  { id: "lab-staff", name: "Lab Staff", pin: "2222" },
  { id: "it-manager", name: "IT Manager", pin: "3333" },
];