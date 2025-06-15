export interface KeyFeature {
  title: string
  description: string
}

export interface ProjectHistory {
  year: string
  title: string
  description: string
}

export interface GetInvolved {
  description: string
  ways: string[]
  callToAction: string
}

export interface MissionContent {
  mission: string
  whoItsFor: string
}

export type Leaders = {
  [key: string]: string
}

export type TechnologySection = {
  section: string
  tools: {
    [toolName: string]: {
      icon: string
      url: string
    }
  }
}
