import type { IconType } from 'react-icons'
import {
  FaDiscord,
  FaFacebook,
  FaGoogle,
  FaLinkedin,
  FaMeetup,
  FaSlack,
  FaXTwitter,
  FaYoutube,
  FaClock,
  FaComment,
  FaStar,
  FaUser,
  FaAward,
  FaBug,
  FaCertificate,
  FaCity,
  FaCodeFork,
  FaEgg,
  FaFlag,
  FaFlask,
  FaMedal,
  FaRibbon,
} from 'react-icons/fa6'

export const BADGE_CLASS_MAP: Record<string, IconType> = {
  award: FaAward,
  bugSlash: FaBug,
  certificate: FaCertificate,
  medal: FaMedal,
  ribbon: FaRibbon,
  star: FaStar,
} as const

export const ICONS = {
  starsCount: {
    label: 'GitHub stars',
    icon: FaStar,
  },
  forksCount: {
    label: 'GitHub forks',
    icon: FaCodeFork,
  },
  contributorsCount: {
    label: 'GitHub contributors',
    icon: FaUser,
  },
  createdAt: {
    label: 'Creation date',
    icon: FaClock,
  },
  commentsCount: {
    label: 'Comments count',
    icon: FaComment,
  },
} as const

export type IconKeys = keyof typeof ICONS

export const level = {
  incubator: {
    color: '#53AAE5',
    icon: FaEgg,
    level: 'Incubator',
  },
  lab: {
    color: '#FFA500',
    icon: FaFlask,
    level: 'Lab',
  },
  production: {
    color: '#800080',
    icon: FaCity,
    level: 'Production',
  },
  flagship: {
    color: '#38a047',
    icon: FaFlag,
    level: 'Flagship',
  },
}

export const urlMappings = [
  { key: 'youtube.com', title: 'YouTube', icon: FaYoutube },
  { key: 'x.com', title: 'X (formerly Twitter)', icon: FaXTwitter },
  { key: 'google.com', title: 'Google', icon: FaGoogle },
  { key: 'meetup.com', title: 'Meetup', icon: FaMeetup },
  { key: 'linkedin.com', title: 'LinkedIn', icon: FaLinkedin },
  { key: 'facebook.com', title: 'Facebook', icon: FaFacebook },
  { key: 'discord.com', title: 'Discord', icon: FaDiscord },
  { key: 'slack.com', title: 'Slack', icon: FaSlack },
]
