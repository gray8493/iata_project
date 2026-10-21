import { Module } from '@nestjs/common';
import { GitHubReleaseService } from './github-release.service';
import { SystemController } from './system.controller';
import { SystemService } from './system.service';

@Module({
  controllers: [SystemController],
  providers: [SystemService, GitHubReleaseService],
})
export class SystemModule {}
