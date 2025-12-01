"""
Waste inventory tracking for lunar mission simulations.

Tracks accumulation and processing of waste streams over time.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import json

from lunarecycle.waste.streams import WasteItem, WasteCategory, WasteStream


@dataclass
class InventoryEntry:
    """Single entry in the waste inventory."""
    waste_item: WasteItem
    quantity_kg: float
    accumulated_date: datetime
    processed: bool = False
    processed_date: Optional[datetime] = None


@dataclass
class WasteInventory:
    """
    Manages waste accumulation and tracking for a lunar mission.

    Tracks what waste has been generated, processed, and remaining.
    """
    crew_size: int = 4
    mission_start: datetime = field(default_factory=datetime.now)
    entries: list[InventoryEntry] = field(default_factory=list)

    # Track totals
    total_generated_kg: float = 0.0
    total_processed_kg: float = 0.0
    total_remaining_kg: float = 0.0

    def add_daily_waste(self, current_date: datetime, waste_items: Optional[list[WasteItem]] = None):
        """
        Add one day's worth of waste generation.

        Args:
            current_date: The simulation date
            waste_items: List of waste items to generate. If None, uses all items.
        """
        if waste_items is None:
            waste_items = WasteStream.get_all_items()

        for item in waste_items:
            daily_mass = item.mass_per_unit_kg * item.generation_rate_per_crew_day * self.crew_size
            entry = InventoryEntry(
                waste_item=item,
                quantity_kg=daily_mass,
                accumulated_date=current_date
            )
            self.entries.append(entry)
            self.total_generated_kg += daily_mass
            self.total_remaining_kg += daily_mass

    def simulate_accumulation(self, days: int, waste_items: Optional[list[WasteItem]] = None):
        """
        Simulate waste accumulation over multiple days.

        Args:
            days: Number of days to simulate
            waste_items: List of waste items to include
        """
        for day in range(days):
            current_date = self.mission_start + timedelta(days=day)
            self.add_daily_waste(current_date, waste_items)

    def process_waste(self, waste_item: WasteItem, quantity_kg: float,
                      process_date: datetime) -> float:
        """
        Mark waste as processed.

        Args:
            waste_item: The type of waste being processed
            quantity_kg: Amount to process (kg)
            process_date: Date of processing

        Returns:
            Actual amount processed (may be less if not enough available)
        """
        remaining_to_process = quantity_kg
        processed = 0.0

        for entry in self.entries:
            if (entry.waste_item.name == waste_item.name and
                not entry.processed and
                remaining_to_process > 0):

                if entry.quantity_kg <= remaining_to_process:
                    # Process entire entry
                    entry.processed = True
                    entry.processed_date = process_date
                    processed += entry.quantity_kg
                    remaining_to_process -= entry.quantity_kg
                else:
                    # Partial processing - split the entry
                    processed_entry = InventoryEntry(
                        waste_item=entry.waste_item,
                        quantity_kg=remaining_to_process,
                        accumulated_date=entry.accumulated_date,
                        processed=True,
                        processed_date=process_date
                    )
                    entry.quantity_kg -= remaining_to_process
                    self.entries.append(processed_entry)
                    processed += remaining_to_process
                    remaining_to_process = 0

        self.total_processed_kg += processed
        self.total_remaining_kg -= processed
        return processed

    def get_unprocessed_by_category(self, category: WasteCategory) -> float:
        """Get total unprocessed waste mass for a category (kg)."""
        return sum(
            entry.quantity_kg for entry in self.entries
            if entry.waste_item.category == category and not entry.processed
        )

    def get_unprocessed_by_item(self, item_name: str) -> float:
        """Get total unprocessed waste mass for a specific item (kg)."""
        return sum(
            entry.quantity_kg for entry in self.entries
            if entry.waste_item.name == item_name and not entry.processed
        )

    def get_total_unprocessed(self) -> float:
        """Get total unprocessed waste mass (kg)."""
        return sum(
            entry.quantity_kg for entry in self.entries if not entry.processed
        )

    def get_category_summary(self) -> dict[WasteCategory, dict]:
        """Get summary statistics by waste category."""
        summary = {}
        for category in WasteCategory:
            cat_entries = [e for e in self.entries if e.waste_item.category == category]
            if cat_entries:
                total = sum(e.quantity_kg for e in cat_entries)
                processed = sum(e.quantity_kg for e in cat_entries if e.processed)
                summary[category] = {
                    "total_kg": total,
                    "processed_kg": processed,
                    "remaining_kg": total - processed,
                    "processing_rate": processed / total if total > 0 else 0.0
                }
        return summary

    def get_item_summary(self) -> dict[str, dict]:
        """Get summary statistics by waste item."""
        summary = {}
        for item in WasteStream.get_all_items():
            item_entries = [e for e in self.entries if e.waste_item.name == item.name]
            if item_entries:
                total = sum(e.quantity_kg for e in item_entries)
                processed = sum(e.quantity_kg for e in item_entries if e.processed)
                summary[item.name] = {
                    "category": item.category.name,
                    "difficulty": item.difficulty.value,
                    "total_kg": total,
                    "processed_kg": processed,
                    "remaining_kg": total - processed,
                    "processing_rate": processed / total if total > 0 else 0.0
                }
        return summary

    def to_dict(self) -> dict:
        """Convert inventory to dictionary for serialization."""
        return {
            "crew_size": self.crew_size,
            "mission_start": self.mission_start.isoformat(),
            "total_generated_kg": self.total_generated_kg,
            "total_processed_kg": self.total_processed_kg,
            "total_remaining_kg": self.total_remaining_kg,
            "category_summary": {
                cat.name: data for cat, data in self.get_category_summary().items()
            },
            "item_summary": self.get_item_summary()
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert inventory to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def print_summary(self):
        """Print a formatted summary of the inventory."""
        print("\n" + "=" * 60)
        print("WASTE INVENTORY SUMMARY")
        print("=" * 60)
        print(f"Crew Size: {self.crew_size}")
        print(f"Mission Start: {self.mission_start.strftime('%Y-%m-%d')}")
        print(f"\nTotal Generated: {self.total_generated_kg:.2f} kg")
        print(f"Total Processed: {self.total_processed_kg:.2f} kg")
        print(f"Total Remaining: {self.total_remaining_kg:.2f} kg")
        print(f"Overall Processing Rate: {self.total_processed_kg / self.total_generated_kg * 100:.1f}%" if self.total_generated_kg > 0 else "N/A")

        print("\n" + "-" * 60)
        print("BY CATEGORY:")
        print("-" * 60)
        for category, data in self.get_category_summary().items():
            print(f"\n{category.name}:")
            print(f"  Total: {data['total_kg']:.2f} kg")
            print(f"  Processed: {data['processed_kg']:.2f} kg ({data['processing_rate']*100:.1f}%)")
            print(f"  Remaining: {data['remaining_kg']:.2f} kg")

        print("\n" + "=" * 60)
