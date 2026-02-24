# Ranger Deck Composition Rules

This document summarizes the rules for Ranger character creation and deck composition based on the Earthborne Rangers rulebook.

## Ranger Character Components

### 1. Personality Cards
- **Selection**: Choose 4 unique personality cards (one from each aspect: AWA, FIT, FOC, SPI)
- **Deck Addition**: Each selected card is added **twice** to the Ranger deck
- **Total in Deck**: 8 cards (4 unique × 2 copies each)

### 2. Background
- **Background Sets**: Artisan, Forager, Shepherd, or Traveler
- **Available Cards**: Each background set contains 9 unique cards
- **Selection**: Choose 5 cards from your chosen background set
- **Deck Addition**: Each selected card is added **twice** to the Ranger deck
- **Total in Deck**: 10 cards (5 unique × 2 copies each)

### 3. Specialty
- **Specialty Sets**: Artificer, Conciliator, Explorer, or Shaper
- **Available Cards**: Each specialty set contains 14 unique cards
- **Selection**: Choose 5 cards from your chosen specialty set
- **Deck Addition**: Each selected card is added **twice** to the Ranger deck
- **Total in Deck**: 10 cards (5 unique × 2 copies each)

### 4. Role Card
- **Source**: Each specialty includes 2 role cards
- **Selection**: Choose 1 role card from your specialty
- **Important**: Role cards do NOT go in the deck - they start the game in play
- **Function**: Provides a special, repeatable ability

### 5. Outside Interest
- **Selection**: Choose 1 card from ANY specialty or background set
- **Restrictions**: Cannot be a role card or have the expert trait
- **Deck Addition**: Add **two copies** of this card to the Ranger deck
- **Total in Deck**: 2 cards (1 unique × 2 copies)
- **Purpose**: Represents hobbies and passions outside of day-to-day Ranger life

## Data Model Fields

The Ranger model stores:
- `personality`: JSON array of 4 unique personality card names
- `background`: String - background set name (Artisan/Forager/Shepherd/Traveler)
- `background_cards`: JSON array of 5 unique background card names
- `specialty`: String - specialty set name (Artificer/Conciliator/Explorer/Shaper)
- `specialty_cards`: JSON array of 5 unique specialty card names
- `role`: String - role card name (from specialty, not in deck)
- `outside_interest`: String - outside interest card name (from any specialty/background, not role/expert)
- `current_decklist`: JSON array of all current deck cards

## Deck Composition Summary

A starting Ranger deck contains:
- 8 personality cards (4 unique × 2 copies)
- 10 background cards (5 unique × 2 copies)
- 10 specialty cards (5 unique × 2 copies)
- 2 outside interest cards (1 unique × 2 copies)
- **Total: 30 cards minimum**

Plus any additional cards acquired during gameplay (trades, rewards, etc.)

The role card is NOT in the deck but starts in play.
