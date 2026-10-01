import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors, FontSize, BorderRadius, Spacing } from '../constants/theme';

interface SentimentBadgeProps {
  sentiment: string | null;
  size?: 'sm' | 'md' | 'lg';
}

export default function SentimentBadge({ sentiment, size = 'md' }: SentimentBadgeProps) {
  const getSentimentStyle = () => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return { bg: Colors.positiveLight, color: Colors.positive, label: 'Pozitif' };
      case 'negative':
        return { bg: Colors.negativeLight, color: Colors.negative, label: 'Negatif' };
      case 'neutral':
        return { bg: Colors.neutralLight, color: Colors.neutral, label: 'Nötr' };
      default:
        return { bg: Colors.backgroundCard, color: Colors.textMuted, label: 'N/A' };
    }
  };

  const style = getSentimentStyle();

  const fontSize = size === 'sm' ? FontSize.xs : size === 'lg' ? FontSize.md : FontSize.sm;
  const paddingH = size === 'sm' ? Spacing.sm : size === 'lg' ? Spacing.lg : Spacing.md;
  const paddingV = size === 'sm' ? 2 : size === 'lg' ? 6 : 4;

  return (
    <View style={[styles.badge, { backgroundColor: style.bg, paddingHorizontal: paddingH, paddingVertical: paddingV }]}>
      <View style={[styles.dot, { backgroundColor: style.color }]} />
      <Text style={[styles.text, { color: style.color, fontSize }]}>{style.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: BorderRadius.full,
    alignSelf: 'flex-start',
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 6,
  },
  text: {
    fontWeight: '600',
    letterSpacing: 0.3,
  },
});
