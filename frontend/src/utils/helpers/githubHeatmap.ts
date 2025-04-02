import { addWeeks } from 'date-fns/addWeeks'
import { format } from 'date-fns/format'
import { getMonth } from 'date-fns/getMonth'
import { isAfter } from 'date-fns/isAfter'
import { isBefore } from 'date-fns/isBefore'
import { parseISO } from 'date-fns/parseISO'
import { setDay } from 'date-fns/setDay'
import { startOfWeek } from 'date-fns/startOfWeek'

const endDate = new Date()
endDate.setDate(endDate.getDate())

const startDate = new Date(endDate)
startDate.setDate(endDate.getDate() - 7 * 52 - 1)

export interface HeatmapData {
  years: DataStructYear[]
  contributions: []
}

const getIntensity = (count) => {
  if (count === 0) return '0'
  if (count <= 3) return '1'
  if (count <= 6) return '2'
  if (count <= 10) return '3'
  return '4'
}

export const fetchHeatmapData = async (username) => {
  try {
    const response = await fetch(`https://github-contributions-api.jogruber.de/v4/${username}`)
    const heatmapData = await response.json()
    if (!heatmapData.contributions) {
      return {}
    }
    heatmapData.contributions = heatmapData.contributions.filter(
      (item) => new Date(item.date) <= endDate && new Date(item.date) >= startDate
    )

    const allDates = []
    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
      allDates.push(format(d, 'yyyy-MM-dd'))
    }

    const transformedContributions = allDates.map((date) => {
      const contribution = heatmapData.contributions.find((c) => c.date === date)
      return contribution
        ? {
            date: contribution.date,
            count: contribution.count,
            intensity: getIntensity(contribution.count),
          }
        : {
            date: date,
            count: 0,
            intensity: '0',
          }
    })

    return {
      years: [
        {
          year: '2024',
        },
      ],
      contributions: transformedContributions,
    }
  } catch (err) {
    return err.message
  }
}


const themes = {
  blue: {
    background: '#1a2233',
    text: '#FFFFFF',
    meta: '#A6B1C1',
    grade4: '#2a70d8',
    grade3: '#4682b4',
    grade2: '#5f87a8',
    grade1: '#46627b',
    grade0: '#202A37',
  },
  blueRed: {
    background: '#1a2233',
    text: '#FFFFFF',
    meta: '#A6B1C1',
    grade4: '#e64a4a',
    grade3: '#4682b4',
    grade2: '#5f87a8',
    grade1: '#46627b',
    grade0: '#202A37',
  }
}

interface DataStructYear {
  year: string
  total: number
  range: {
    start: string
    end: string
  }
}
interface DataStructContribution {
  date: string
  count: number
  color: string
  intensity: number
}
interface DataStruct {
  years: DataStructYear[]
  contributions: DataStructContribution[]
}
interface GraphEntry {
  date: string
  info?: DataStructContribution
}
interface Options {
  themeName?: keyof typeof themes
  customTheme?: Theme
  skipHeader?: boolean
  skipAxisLabel?: boolean
  username: string
  data: DataStruct
  fontFace?: string
  footerText?: string
  theme?: string
  showTooltips?: boolean
}
interface DrawYearOptions extends Options {
  year: DataStructYear
  offsetX?: number
  offsetY?: number
}
interface DrawMetadataOptions extends Options {
  width: number
  height: number
}
interface Theme {
  background: string
  text: string
  meta: string
  grade4: string
  grade3: string
  grade2: string
  grade1: string
  grade0: string
}

function getPixelRatio() {
  if (typeof window === 'undefined') {
    return 1
  }
  return window.devicePixelRatio || 1
}

const DATE_FORMAT = 'yyyy-MM-dd'

const boxWidth = 12
const boxMargin = 3
const textHeight = 15
const defaultFontFace = 'IBM Plex Mono'
const headerHeight = 40
const canvasMargin = 20
const yearHeight = textHeight + (boxWidth + boxMargin) * 8 + canvasMargin
const scaleFactor = getPixelRatio()

function getTheme(opts: Options): Theme {
  const { themeName } = opts
  const name = themeName ?? 'blue'
  return themes[name] ?? themes.blue
}

function getDateInfo(data: DataStruct, date: string) {
  return data.contributions.find((contrib) => contrib.date === date)
}

function drawYear(ctx: CanvasRenderingContext2D, opts: DrawYearOptions) {
  const { offsetX = 0, offsetY = 0, data, fontFace = defaultFontFace } = opts
  const theme = getTheme(opts)

  let nextDate = startOfWeek(startDate)
  const firstRowDates: GraphEntry[] = []
  const graphEntries: GraphEntry[][] = []

  while (isBefore(nextDate, endDate)) {
    const date = format(nextDate, DATE_FORMAT)
    firstRowDates.push({
      date,
      info: getDateInfo(data, date),
    })
    nextDate = addWeeks(nextDate, 1)
  }

  graphEntries.push(firstRowDates)

  for (let i = 1; i < 7; i += 1) {
    graphEntries.push(
      firstRowDates.map((dateObj) => {
        const date = format(setDay(parseISO(dateObj.date), i), DATE_FORMAT)
        return {
          date,
          info: getDateInfo(data, date),
        }
      })
    )
  }
  if (!opts.skipHeader) {
    ctx.textBaseline = 'hanging'
    ctx.fillStyle = theme.text
    ctx.font = `10px '${fontFace}'`
  }


  const cellsData = []

  for (let y = 0; y < graphEntries.length; y += 1) {
    for (let x = 0; x < graphEntries[y].length; x += 1) {
      const day = graphEntries[y][x]
      const cellDate = parseISO(day.date)
      if (isAfter(cellDate, endDate) || !day.info) {
        continue
      }

      const color = theme[`grade${day.info.intensity}`]
      ctx.fillStyle = color
      const cellX = offsetX + (boxWidth + boxMargin) * x
      const cellY = offsetY + textHeight + (boxWidth + boxMargin) * y
      const cellRadius = 2

      ctx.beginPath()
      ctx.moveTo(cellX + cellRadius, cellY)
      ctx.arcTo(cellX + boxWidth, cellY, cellX + boxWidth, cellY + boxWidth, cellRadius)
      ctx.arcTo(cellX + boxWidth, cellY + boxWidth, cellX, cellY + boxWidth, cellRadius)
      ctx.arcTo(cellX, cellY + boxWidth, cellX, cellY, cellRadius)
      ctx.arcTo(cellX, cellY, cellX + boxWidth, cellY, cellRadius)
      ctx.closePath()
      ctx.fillStyle = color
      ctx.fill()


      if (opts.showTooltips) {
        cellsData.push({
          x: cellX,
          y: cellY,
          width: boxWidth,
          height: boxWidth,
          date: day.date,
          count: day.info.count
        })
      }
    }
  }

  // Draw Month Label
  let lastCountedMonth = 0
  for (let y = 0; y < graphEntries[0].length; y += 1) {
    const date = parseISO(graphEntries[0][y].date)
    const month = getMonth(date) + 1
    const firstMonthIsDec = month === 12 && y === 0
    const monthChanged = month !== lastCountedMonth
    if (!opts.skipAxisLabel && monthChanged && !firstMonthIsDec) {
      ctx.fillStyle = theme.meta
      lastCountedMonth = month
    }
  }

  return cellsData
}

function drawMetaData(ctx: CanvasRenderingContext2D, opts: DrawMetadataOptions) {
  const { width, height, fontFace = defaultFontFace } = opts
  const theme = getTheme(opts)
  ctx.fillStyle = theme.background
  ctx.fillRect(0, 0, width, height)

  ctx.fillStyle = theme.text
  ctx.textBaseline = 'hanging'
  ctx.font = `12px '${fontFace}'`
  ctx.fillText('Contributions:', canvasMargin, 20)

  const legendBoxSize = 12
  const legendSpacing = 60


  for (let i = 0; i <= 4; i++) {
    const boxX = canvasMargin + 120 + i * legendSpacing
    const boxY = 20

    ctx.fillStyle = theme[`grade${i}`]
    ctx.beginPath()
    ctx.rect(boxX, boxY, legendBoxSize, legendBoxSize)
    ctx.fill()

    ctx.fillStyle = theme.text
    let label = ''
    if (i === 0) label = 'No activity'
    else if (i === 1) label = '1-3'
    else if (i === 2) label = '4-6'
    else if (i === 3) label = '7-10'
    else label = '10+'

    ctx.fillText(label, boxX + legendBoxSize + 5, boxY + 2)
  }
  ctx.beginPath()
  ctx.moveTo(canvasMargin, 55)
  ctx.lineTo(width - canvasMargin, 55)
  ctx.strokeStyle = theme.grade0
  ctx.stroke()
}

export function drawContributions(canvas: HTMLCanvasElement, opts: Options) {
  const { data } = opts
  let headerOffset = 0
  if (!opts.skipHeader) {
    headerOffset = headerHeight
  }
  const height = data.years.length * yearHeight + canvasMargin + headerOffset + 10
  const width = 53 * (boxWidth + boxMargin) + canvasMargin * 2

  canvas.width = width * scaleFactor
  canvas.height = height * scaleFactor

  const ctx = canvas.getContext('2d')

  if (!ctx) {
    throw new Error('Could not get 2d context from Canvas')
  }

  ctx.scale(scaleFactor, scaleFactor)
  ctx.textBaseline = 'hanging'
  if (!opts.skipHeader) {
    drawMetaData(ctx, {
      ...opts,
      width,
      height,
      data,
    })
  }

  let allCellsData = []
  data.years.forEach((year, i) => {
    const offsetY = yearHeight * i + canvasMargin + headerOffset + 10
    const offsetX = canvasMargin
    const cellsData = drawYear(ctx, {
      ...opts,
      year,
      offsetX,
      offsetY,
      data,
    })
    if (cellsData) {
      allCellsData = [...allCellsData, ...cellsData]
    }
  })

  if (opts.showTooltips && typeof window !== 'undefined') {
    const tooltip = document.createElement('div')
    tooltip.style.position = 'absolute'
    tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.8)'
    tooltip.style.color = 'white'
    tooltip.style.padding = '5px 10px'
    tooltip.style.borderRadius = '3px'
    tooltip.style.fontSize = '14px'
    tooltip.style.pointerEvents = 'none'
    tooltip.style.opacity = '0'
    tooltip.style.transition = 'opacity 0.2s'
    tooltip.style.zIndex = '1000'
    document.body.appendChild(tooltip)

    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect()
      const x = (e.clientX - rect.left) / scaleFactor
      const y = (e.clientY - rect.top) / scaleFactor

      let found = false
      allCellsData.forEach(cell => {
        if (
          x >= cell.x &&
          x <= cell.x + cell.width &&
          y >= cell.y &&
          y <= cell.y + cell.height
        ) {
          const date = new Date(cell.date).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
          })

          tooltip.innerHTML = `
            <div>${date}</div>
            <div>${cell.count} contribution${cell.count !== 1 ? 's' : ''}</div>
          `
          tooltip.style.left = `${e.clientX + 10}px`
          tooltip.style.top = `${e.clientY + 10}px`
          tooltip.style.opacity = '1'
          found = true
        }
      })

      if (!found) {
        tooltip.style.opacity = '0'
      }
    })

    canvas.addEventListener('mouseout', () => {
      tooltip.style.opacity = '0'
    })


    canvas.addEventListener('click', (e) => {
      const rect = canvas.getBoundingClientRect()
      const x = (e.clientX - rect.left) / scaleFactor
      const y = (e.clientY - rect.top) / scaleFactor

      allCellsData.forEach(cell => {
        if (
          x >= cell.x &&
          x <= cell.x + cell.width &&
          y >= cell.y &&
          y <= cell.y + cell.height
        ) {

          const event = new CustomEvent('heatmap-cell-click', {
            detail: {
              date: cell.date,
              count: cell.count
            }
          })
          canvas.dispatchEvent(event)
        }
      })
    })
  }
}
