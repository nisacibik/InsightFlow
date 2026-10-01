import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, RefreshControl } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, BorderRadius, Spacing } from '../../constants/theme';
import api, { turkishApiError } from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export default function DatasetsScreen() {
  const router = useRouter();
  const [datasets, setDatasets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDatasets = async () => {
    try {
      setError(null);
      const result = await api.getDatasets();
      setDatasets(Array.isArray(result) ? result : []);
    } catch (err) {
      console.error(err);
      setError(turkishApiError(err));
      setDatasets([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchDatasets();
  };

  if (loading) return <LoadingSpinner message="Datasets yükleniyor..." />;

  const getSubsectorIcon = (subsector: string): keyof typeof Ionicons.glyphMap => {
    switch (subsector?.toLowerCase()) {
      case 'ai': return 'sparkles';
      case 'software': return 'code-slash';
      case 'mobil uygulamalar': return 'phone-portrait';
      default: return 'folder';
    }
  };

  const getSubsectorColor = (subsector: string) => {
    switch (subsector?.toLowerCase()) {
      case 'ai': return Colors.primary;
      case 'software': return Colors.accent;
      case 'mobil uygulamalar': return Colors.info;
      default: return Colors.textMuted;
    }
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.primary} />}
      showsVerticalScrollIndicator={false}
    >
      <Text style={styles.pageTitle}>Veri Kümeleri</Text>
      <Text style={styles.pageSubtitle}>{datasets.length} dataset mevcut</Text>
      {error ? <Text style={{ color: Colors.negative, marginBottom: 12 }}>{error}</Text> : null}
      {datasets.length === 0 && !error ? (
        <EmptyState message="Henüz veri bulunmuyor." icon="layers-outline" />
      ) : null}

      {datasets.map((dataset) => {
        const color = getSubsectorColor(dataset.subsector);
        const icon = getSubsectorIcon(dataset.subsector);

        return (
          <TouchableOpacity
            key={dataset.id}
            style={styles.card}
            activeOpacity={0.7}
            onPress={() => router.push(`/dataset/${dataset.id}`)}
          >
            <View style={styles.cardHeader}>
              <View style={[styles.iconContainer, { backgroundColor: `${color}20` }]}>
                <Ionicons name={icon} size={24} color={color} />
              </View>
              <View style={styles.cardHeaderText}>
                <Text style={styles.cardTitle} numberOfLines={2}>{dataset.name}</Text>
                <View style={[styles.subsectorBadge, { backgroundColor: `${color}15` }]}>
                  <Text style={[styles.subsectorText, { color }]}>{dataset.subsector}</Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={20} color={Colors.textMuted} />
            </View>

            {dataset.description && (
              <Text style={styles.description} numberOfLines={2}>
                {dataset.description}
              </Text>
            )}

            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Ionicons name="chatbubbles-outline" size={14} color={Colors.textMuted} />
                <Text style={styles.statValue}>{parseInt(dataset.actual_review_count).toLocaleString()}</Text>
                <Text style={styles.statLabel}>yorum</Text>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statItem}>
                <Ionicons name="calendar-outline" size={14} color={Colors.textMuted} />
                <Text style={styles.statValue}>{dataset.data_period}</Text>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statItem}>
                <Ionicons name="document-outline" size={14} color={Colors.textMuted} />
                <Text style={styles.statValue}>{dataset.license || 'N/A'}</Text>
              </View>
            </View>
          </TouchableOpacity>
        );
      })}

      <View style={{ height: 30 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    padding: Spacing.lg,
  },
  pageTitle: {
    fontSize: FontSize.xxxl,
    fontWeight: '800',
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  pageSubtitle: {
    fontSize: FontSize.md,
    color: Colors.textSecondary,
    marginBottom: Spacing.xl,
  },
  card: {
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.lg,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.md,
  },
  cardHeaderText: {
    flex: 1,
  },
  cardTitle: {
    fontSize: FontSize.lg,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  subsectorBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    borderRadius: BorderRadius.full,
  },
  subsectorText: {
    fontSize: FontSize.xs,
    fontWeight: '600',
  },
  description: {
    fontSize: FontSize.md,
    color: Colors.textSecondary,
    lineHeight: 20,
    marginBottom: Spacing.md,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    flex: 1,
    justifyContent: 'center',
  },
  statValue: {
    fontSize: FontSize.sm,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
  statLabel: {
    fontSize: FontSize.xs,
    color: Colors.textMuted,
  },
  statDivider: {
    width: 1,
    height: 20,
    backgroundColor: Colors.border,
  },
});
