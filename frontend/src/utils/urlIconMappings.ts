import {
  faDiscord,
  faInstagram,
  faLinkedin,
  faYoutube,
  faXTwitter,
  faMeetup,
  faSlack,
  faFacebook,
  faTelegram,
  faGoogle,
  faBluesky,
  faWhatsapp,
  faTiktok,
  faGithub,
  faSlideshare,
  faSpeakerDeck,
  faVimeo,
  faTwitch,
  faMedium,
} from '@fortawesome/free-brands-svg-icons'
import { faGlobe } from '@fortawesome/free-solid-svg-icons'

export const getSocialIcon = (url: string) => {
  const hostname = new URL(url).hostname.toLowerCase()

  if (hostname.includes('discord')) return faDiscord
  if (hostname.includes('instagram')) return faInstagram
  if (hostname.includes('linkedin')) return faLinkedin
  if (hostname.includes('youtube')) return faYoutube
  if (hostname.includes('meetup')) return faMeetup
  if (hostname.includes('slack')) return faSlack
  if (hostname.includes('facebook')) return faFacebook
  if (hostname.includes('telegram') || hostname.includes('t.me')) return faTelegram
  if (hostname.includes('google')) return faGoogle
  if (hostname.includes('bsky')) return faBluesky
  if (hostname.includes('whatsapp')) return faWhatsapp
  if (hostname.includes('tiktok')) return faTiktok
  if (hostname.includes('github')) return faGithub
  if (hostname.includes('slideshare')) return faSlideshare
  if (hostname.includes('speakerdeck')) return faSpeakerDeck
  if (hostname.includes('vimeo')) return faVimeo
  if (hostname.includes('twitch')) return faTwitch
  if (hostname.includes('medium')) return faMedium
  if (hostname === 'x.com' || hostname.endsWith('.x.com') || hostname.includes('twitter')) {
    return faXTwitter
  }

  return faGlobe
}
