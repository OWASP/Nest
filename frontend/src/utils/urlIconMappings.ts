import type { IconType } from 'react-icons'
import {
  FaDiscord,
  FaInstagram,
  FaLinkedin,
  FaYoutube,
  FaMeetup,
  FaSlack,
  FaFacebook,
  FaTelegram,
  FaGoogle,
  FaWhatsapp,
  FaTiktok,
  FaGithub,
  FaSlideshare,
  FaSpeakerDeck,
  FaVimeo,
  FaTwitch,
  FaMedium,
  FaGlobe,
} from 'react-icons/fa'
import { FaXTwitter, FaBluesky } from 'react-icons/fa6'

export const getSocialIcon = (url: string): IconType => {
  const hostname = new URL(url).hostname.toLowerCase()

  if (hostname.includes('discord')) return FaDiscord
  if (hostname.includes('instagram')) return FaInstagram
  if (hostname.includes('linkedin')) return FaLinkedin
  if (hostname.includes('youtube')) return FaYoutube
  if (hostname.includes('meetup')) return FaMeetup
  if (hostname.includes('slack')) return FaSlack
  if (hostname.includes('facebook')) return FaFacebook
  if (hostname.includes('telegram') || hostname.includes('t.me')) return FaTelegram
  if (hostname.includes('google')) return FaGoogle
  if (hostname.includes('bsky')) return FaBluesky
  if (hostname.includes('whatsapp')) return FaWhatsapp
  if (hostname.includes('tiktok')) return FaTiktok
  if (hostname.includes('github')) return FaGithub
  if (hostname.includes('slideshare')) return FaSlideshare
  if (hostname.includes('speakerdeck')) return FaSpeakerDeck
  if (hostname.includes('vimeo')) return FaVimeo
  if (hostname.includes('twitch')) return FaTwitch
  if (hostname.includes('medium')) return FaMedium
  if (hostname === 'x.com' || hostname.endsWith('.x.com') || hostname.includes('twitter')) {
    return FaXTwitter
  }

  return FaGlobe
}
