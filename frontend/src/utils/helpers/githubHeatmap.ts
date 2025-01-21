import { drawContributions as draw } from 'github-contributions-canvas'
export const drawContributions = (canvas, { data, username, theme }) => {
  draw(canvas, {
    data,
    username,
    themeName: theme,
  })
}

const getColor = (count) => {
  if (count === 0) return '#ebedf0'
  return count >= 5 ? '#2cbe4e' : count >= 3 ? '#ffb22e' : '#ebedf0'
}

const getIntensity = (count) => {
  if (count === 0) {
    return '0'
  } else if (count == 1 || count == 2) {
    return '1'
  } else if (count >= 3 && count <= 5) {
    return '2'
  } else if (count >= 6 && count <= 10) {
    return '3'
  } else {
    return '4'
  }
}

export const fetchHeatmapData = async (username) => {
  try {
    const data = await fetch(`https://github-contributions-api.jogruber.de/v4/${username}`)
    const data2 = await data.json()
    data2.contributions = data2.contributions.filter((item) => item.date.split('-')[0] === '2024')

    const transformedContributions = []
    const allDates = data2.contributions.map((contribution) => contribution.date)

    for (let date of allDates) {
      const contribution = data2.contributions.find((c) => c.date === date)
      if (contribution) {
        transformedContributions.push({
          date: contribution.date,
          count: contribution.count,
          color: getColor(contribution.count),
          intensity: getIntensity(contribution.count),
        })
      } else {
        transformedContributions.push({
          date: date,
          count: 0,
          color: '#ebedf0',
          intensity: '0',
        })
      }
    }
    return {
      years: [
        {
          year: '2024',
          total: data2.total['2024'],
          range: {
            start: '2024-01-07',
            end: '2024-12-28',
          },
        },
      ],
      contributions: transformedContributions,
    }
  } catch (err) {
    return err.message
  }
}
