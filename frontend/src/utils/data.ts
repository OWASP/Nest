import type { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faDiscord,
  faFacebook,
  faGoogle,
  faLinkedin,
  faMeetup,
  faSlack,
  faXTwitter,
  faYoutube,
} from '@fortawesome/free-brands-svg-icons'
import {
  faClock,
  faComment,
  faLightbulb,
  faStar,
  faUser,
} from '@fortawesome/free-regular-svg-icons'
import {
  faArrowsRotate,
  faAward,
  faBug,
  faCertificate,
  faCity,
  faCode,
  faCodeFork,
  faEgg,
  faFlag,
  faFlask,
  faGlobe,
  faMedal,
  faMoon,
  faPeopleGroup,
  faRibbon,
  faRightToBracket,
  faStar as faSolidStar,
  faSun,
  faWandMagicSparkles,
  faX,
} from '@fortawesome/free-solid-svg-icons'

library.add(
  faArrowsRotate,
  faAward,
  faBug,
  faCertificate,
  faCity,
  faClock,
  faCode,
  faCodeFork,
  faComment,
  faDiscord,
  faEgg,
  faFacebook,
  faFlag,
  faFlask,
  faGlobe,
  faGoogle,
  faLightbulb,
  faLinkedin,
  faMedal,
  faMeetup,
  faMoon,
  faPeopleGroup,
  faRibbon,
  faRightToBracket,
  faSlack,
  faStar,
  faSun,
  faUser,
  faWandMagicSparkles,
  faX,
  faXTwitter,
  faYoutube
)

export const BADGE_CLASS_MAP: Record<string, IconDefinition> = {
  award: faAward,
  bugSlash: faBug,
  certificate: faCertificate,
  medal: faMedal,
  ribbon: faRibbon,
  star: faSolidStar,
} as const

export const ICONS = {
  starsCount: {
    label: 'GitHub stars',
    icon: 'fa-regular fa-star',
  },
  forksCount: {
    label: 'GitHub forks',
    icon: 'fa-solid fa-code-fork',
  },
  contributorsCount: {
    label: 'GitHub contributors',
    icon: 'fa-regular fa-user',
  },
  createdAt: {
    label: 'Creation date',
    icon: 'fa-regular fa-clock',
  },
  commentsCount: {
    label: 'Comments count',
    icon: 'fa-regular fa-comment',
  },
} as const

export type IconKeys = keyof typeof ICONS

export const level = {
  incubator: {
    color: '#53AAE5',
    icon: ' text-white fa-solid fa-egg ',
    level: 'Incubator',
  },
  lab: {
    color: '#FFA500',
    icon: ' text-white fa-solid fa-flask',
    level: 'Lab',
  },
  production: {
    color: '#800080',
    icon: ' text-white fa-solid fa-city',
    level: 'Production',
  },
  flagship: {
    color: '#38a047',
    icon: ' text-white fa-solid fa-flag',
    level: 'Flagship',
  },
}

export const urlMappings = [
  { key: 'youtube.com', title: 'YouTube', icon: 'fa-brands fa-youtube' },
  {
    key: 'x.com',
    title: 'X (formerly Twitter)',
    icon: 'fa-brands fa-x-twitter',
  },
  { key: 'google.com', title: 'Google', icon: 'fa-brands fa-google' },
  { key: 'meetup.com', title: 'Meetup', icon: 'fa-brands fa-meetup' },
  { key: 'linkedin.com', title: 'LinkedIn', icon: 'fa-brands fa-linkedin' },
  { key: 'facebook.com', title: 'Facebook', icon: 'fa-brands fa-facebook' },
  { key: 'discord.com', title: 'Discord', icon: 'fa-brands fa-discord' },
  { key: 'slack.com', title: 'Slack', icon: 'fa-brands fa-slack' },
]
