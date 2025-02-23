import { ProjectTypeGraphql } from "./project";
import { ChapterTypeGraphQL } from "./chapter";

export interface SnapshotType {
  title: string;
  key: string;
  createdAt: string;
  updatedAt: string;
  startAt: string;
  endAt: string;
  newReleases: SnapshotReleaseType[];
  newProjects: ProjectTypeGraphql[];
  newChapters: ChapterTypeGraphQL[];
}

export interface SnapshotReleaseType {
  name: string;
  version: string;
  releaseDate: string;
}
