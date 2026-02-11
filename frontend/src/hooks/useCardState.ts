'use client'

import { useCallback, useEffect, useState } from 'react'

interface CardState {
  isActive: boolean
  isVisited: boolean
}

interface CardStates {
  [key: string]: CardState
}

export const useCardState = (cardKey: string) => {
  const [cardStates, setCardStates] = useState<CardStates>({})
  const [currentCard, setCurrentCard] = useState<string | null>(null)

  // Load visited cards from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem('nest-visited-cards')
      if (stored) {
        const visitedCards = JSON.parse(stored)
        setCardStates(prev => ({
          ...prev,
          ...Object.fromEntries(
            Object.entries(visitedCards).map(([key]) => [key, { isActive: false, isVisited: true }])
          )
        }))
      }
    } catch (error) {
      console.warn('Failed to load visited cards from localStorage:', error)
    }
  }, [])

  // Save visited cards to localStorage whenever they change
  useEffect(() => {
    const visitedCards = Object.entries(cardStates)
      .filter(([_, state]) => state.isVisited)
      .map(([key]) => key)
    
    try {
      localStorage.setItem('nest-visited-cards', JSON.stringify(visitedCards))
    } catch (error) {
      console.warn('Failed to save visited cards to localStorage:', error)
    }
  }, [cardStates])

  const handleCardClick = useCallback((clickedCardKey: string) => {
    // Set active state
    setCurrentCard(clickedCardKey)
    
    // Update card states
    setCardStates(prev => ({
      ...prev,
      [clickedCardKey]: { isActive: true, isVisited: true }
    }))

    // Remove active state after animation
    setTimeout(() => {
      setCurrentCard(null)
      setCardStates(prev => ({
        ...prev,
        [clickedCardKey]: { isActive: false, isVisited: true }
      }))
    }, 150)
  }, [])

  const getCardState = useCallback((key: string): CardState => {
    return cardStates[key] || { isActive: false, isVisited: false }
  }, [cardStates])

  const isCardActive = useCallback((key: string): boolean => {
    return currentCard === key || getCardState(key).isActive
  }, [currentCard, getCardState])

  const isCardVisited = useCallback((key: string): boolean => {
    return getCardState(key).isVisited
  }, [getCardState])

  return {
    handleCardClick,
    isCardActive,
    isCardVisited,
    cardState: getCardState(cardKey)
  }
}
