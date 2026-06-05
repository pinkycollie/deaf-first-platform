import { findById } from "../repositories/userRepo.js";

export async function getUserById(id) {
  return await findById(id);
}
