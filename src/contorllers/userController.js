export async function getUser(req, res, next) {
  try {
    res.json({ id: req.params.id, name: "Example User" });
  } catch (err) {
    next(err);
  }
}
