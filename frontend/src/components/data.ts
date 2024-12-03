import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faDiscord,
  faFacebook,
  faGoogle,
  faLinkedin,
  faMeetup,
  faSlack,
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
  faSlack
)

export const Icons = {
  idx_updated_at: {
    label: 'Last update date',
    icon: 'fa-solid fa-arrows-rotate',
  },
  idx_forks_count: {
    label: 'GitHub forks count',
    icon: 'fa-solid fa-code-fork',
  },
  idx_stars_count: {
    label: 'GitHub stars count',
    icon: 'fa-regular fa-star',
  },
  idx_contributors_count: {
    label: 'GitHub contributors count',
    icon: 'fa-regular fa-user',
  },
  idx_created_at: {
    label: 'Creation date',
    icon: 'fa-regular fa-clock',
  },
  idx_comments_count: {
    label: 'Comments count',
    icon: 'fa-regular fa-comment',
  },
} as const

export type IconKeys = keyof typeof Icons

export const level = {
  incubator: {
    color: '#53AAE5',
    icon: ' text-white fa-solid fa-egg ',
  },
  lab: {
    color: '#FFA500',
    icon: ' text-white fa-solid fa-flask',
  },
  production: {
    color: '#800080',
    icon: ' text-white fa-solid fa-city',
  },
  flagship: {
    color: '#38a047',
    icon: ' text-white fa-solid fa-flag',
  },
}

export const urlMappings = [
  { key: 'youtube.com', title: 'YouTube', icon: 'fa-brands fa-youtube' },
  { key: 'x.com', title: 'X (formerly Twitter)', icon: 'fa-brands fa-x-twitter' },
  { key: 'google.com', title: 'Google', icon: 'fa-brands fa-google' },
  { key: 'meetup.com', title: 'Meetup', icon: 'fa-brands fa-meetup' },
  { key: 'linkedin.com', title: 'LinkedIn', icon: 'fa-brands fa-linkedin' },
  { key: 'facebook.com', title: 'Facebook', icon: 'fa-brands fa-facebook' },
  { key: 'discord.com', title: 'Discord', icon: 'fa-brands fa-discord' },
  { key: 'slack.com', title: 'Slack', icon: 'fa-brands fa-slack' },
]
