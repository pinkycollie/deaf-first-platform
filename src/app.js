import express from "express";
import userRoutes from "./routes/v1/userRoutes.js";
import { errorHandler } from "./handlers/errorHandler.js";

const app = express();

app.use(express.json());

// versioned API
app.use("/v1/users", userRoutes);

// global error handler
app.use(errorHandler);

export default app;
