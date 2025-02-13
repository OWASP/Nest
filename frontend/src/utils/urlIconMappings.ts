import {
  faDiscord,
  faInstagram,
  faLinkedin,
  faYoutube,
  faTwitter as faXTwitter,
  faMeetup,
  faSlack,
} from '@fortawesome/free-brands-svg-icons'
import { faGlobe } from '@fortawesome/free-solid-svg-icons'

export const getSocialIcon = (url) => {
  if (!/^https?:\/\//i.test(url)) {
    url = 'http://' + url
  }

  const hostname = new URL(url).hostname.toLowerCase()

  if (hostname.includes('discord')) return faDiscord
  if (hostname.includes('instagram')) return faInstagram
  if (hostname.includes('linkedin')) return faLinkedin
  if (hostname.includes('youtube')) return faYoutube
  if (hostname.includes('meetup')) return faMeetup
  if (hostname.includes('slack')) return faSlack

  if (hostname === 'x.com' || hostname.endsWith('.x.com') || hostname.includes('twitter')) {
    return faXTwitter
  }

  return faGlobe
}
