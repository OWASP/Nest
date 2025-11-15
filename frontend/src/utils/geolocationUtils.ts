export interface UserLocation {
  latitude: number
  longitude: number
  city?: string
  country?: string
}

interface ChapterCoordinates {
  lat: number | null
  lng: number | null
}

export const calculateDistance = (
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number => {
  const R = 6371
  const dLat = ((lat2 - lat1) * Math.PI) / 180
  const dLon = ((lon2 - lon1) * Math.PI) / 180

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) ** 2

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

export const getUserLocationFromBrowser = (): Promise<UserLocation | null> => {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      // eslint-disable-next-line no-console
      console.warn('Geolocation API not supported')
      resolve(null)
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        })
      },
      (error) => {
        // eslint-disable-next-line no-console
        console.warn('Browser geolocation error:', error.message)
        resolve(null)
      },
      {
        enableHighAccuracy: false,
        timeout: 10000,
        maximumAge: 0,
      }
    )
  })
}

const extractChapterCoordinates = (chapter: Record<string, unknown>): ChapterCoordinates => {
  const lat =
    (chapter._geoloc as Record<string, unknown>)?.lat ??
    (chapter.geoLocation as Record<string, unknown>)?.lat ??
    (chapter.geoLocation as Record<string, unknown>)?.latitude ??
    (chapter.location as Record<string, unknown>)?.lat ??
    null

  const lng =
    (chapter._geoloc as Record<string, unknown>)?.lng ??
    (chapter._geoloc as Record<string, unknown>)?.lon ??
    (chapter.geoLocation as Record<string, unknown>)?.lng ??
    (chapter.geoLocation as Record<string, unknown>)?.lon ??
    (chapter.geoLocation as Record<string, unknown>)?.longitude ??
    (chapter.location as Record<string, unknown>)?.lng ??
    (chapter.location as Record<string, unknown>)?.lon ??
    null

  return { lat: lat as number | null, lng: lng as number | null }
}

/**
 * Sort chapters by distance from user
 */
export const sortChaptersByDistance = (
  chapters: Record<string, unknown>[],
  userLocation: UserLocation
): Array<Record<string, unknown> & { distance: number }> => {
  return chapters
    .map((chapter) => {
      const { lat, lng } = extractChapterCoordinates(chapter)

      if (typeof lat !== 'number' || typeof lng !== 'number') return null

      const distance = calculateDistance(userLocation.latitude, userLocation.longitude, lat, lng)

      return { ...chapter, distance }
    })
    .filter((item) => item !== null) // remove invalid ones
    .sort((a, b) => a!.distance - b!.distance) as Array<
    Record<string, unknown> & { distance: number }
  >
}
