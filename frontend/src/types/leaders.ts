export type LeadersListProps = {
  leaders: string
}

// Maps username to certification strings (e.g., { arkid15r: 'CCSP, CISSP, CSSLP' })
export type LeadersListBlockProps = {
  [key: string]: string
}
