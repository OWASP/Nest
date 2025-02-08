import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faDiscord,
  faFacebook,
  faGoogle,
  faLinkedin,
  faMeetup,
  faSlack,
  faYoutube,
  faXTwitter,
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
  faCity,
  faCode,
  faCodeFork,
  faEgg,
  faFlag,
  faFlask,
  faGlobe,
  faMoon,
  faRightToBracket,
  faWandMagicSparkles,
  faX,
  faPeopleGroup,
  faSun,
} from '@fortawesome/free-solid-svg-icons'

library.add(
  faArrowsRotate,
  faCodeFork,
  faStar,
  faUser,
  faClock,
  faComment,
  faEgg,
  faFlask,
  faCity,
  faFlag,
  faCode,
  faMoon,
  faLightbulb,
  faWandMagicSparkles,
  faGlobe,
  faRightToBracket,
  faYoutube,
  faX,
  faGoogle,
  faMeetup,
  faLinkedin,
  faFacebook,
  faDiscord,
  faSlack,
  faPeopleGroup,
  faXTwitter,
  faSun
)

export const Icons = {
  stars_count: {
    label: 'GitHub stars',
    icon: 'fa-regular fa-star',
  },
  forks_count: {
    label: 'GitHub forks',
    icon: 'fa-solid fa-code-fork',
  },
  contributors_count: {
    label: 'GitHub contributors',
    icon: 'fa-regular fa-user',
  },
  created_at: {
    label: 'Creation date',
    icon: 'fa-regular fa-clock',
  },
  comments_count: {
    label: 'Comments count',
    icon: 'fa-regular fa-comment',
  },
} as const

export type IconKeys = keyof typeof Icons

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
