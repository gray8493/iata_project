import 'reflect-metadata';
import express = require('express');
import { Express, NextFunction, Request, Response } from 'express';
import { NestFactory } from '@nestjs/core';
import { ExpressAdapter } from '@nestjs/platform-express';
import { AppModule } from './app.module';
import { configureApp } from './app.setup';

let serverPromise: Promise<Express> | undefined;

async function createServer(): Promise<Express> {
  const server = express();
  const app = await NestFactory.create(AppModule, new ExpressAdapter(server), { bodyParser: false });
  configureApp(app);
  await app.init();
  return server;
}

export async function serverlessHandler(req: Request, res: Response, next: NextFunction): Promise<void> {
  serverPromise ??= createServer().catch((error) => {
    serverPromise = undefined;
    throw error;
  });
  const server = await serverPromise;
  server(req, res, next);
}
