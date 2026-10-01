import React, { useCallback, useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  TextInput,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, BorderRadius, Spacing } from '../../constants/theme';
import api, { turkishApiError } from '../../services/api';
import ReviewCard from '../../components/ReviewCard';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

const PAGE_SIZE = 20;

const SECTOR_FILTERS = [
  { id: undefined, label: 'Tüm Sektörler' },
  { id: 1, label: 'SaaS' },
  { id: 2, label: 'Yapay Zeka' },
  { id: 3, label: 'Mobil Uygulamalar' },
];

const SENTIMENT_FILTERS = [
  { id: undefined, label: 'Tüm Duygular' },
  { id: 'positive', label: 'Pozitif' },
  { id: 'negative', label: 'Negatif' },
  { id: 'neutral', label: 'Nötr' },
];

const RATING_FILTERS = [
  { id: undefined, label: 'Tümü' },
  { id: 5, label: '5 ★' },
  { id: 4, label: '4 ★' },
  { id: 3, label: '3 ★' },
  { id: 2, label: '2 ★' },
  { id: 1, label: '1 ★' },
];

export default function ReviewsScreen() {
  const router = useRouter();
  const [reviews, setReviews] = useState<any[]>([]);
  const [pagination, setPagination] = useState({ total: 0, has_more: false, offset: 0 });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filtre durumları
  const [search, setSearch] = useState('');
  const [selectedSector, setSelectedSector] = useState<number | undefined>(undefined);
  const [selectedSentiment, setSelectedSentiment] = useState<string | undefined>(undefined);
  const [selectedRating, setSelectedRating] = useState<number | undefined>(undefined);

  const fetchReviews = useCallback(
    async (offset = 0, replace = true) => {
      try {
        setError(null);
        const result = await api.getReviews({
          limit: PAGE_SIZE,
          offset,
          search: search.trim() || undefined,
          dataset_id: selectedSector,
          sentiment: selectedSentiment,
          rating: selectedRating,
          sort: 'newest',
        });
        setReviews((prev) => (replace ? result.data : [...prev, ...result.data]));
        setPagination({
          total: result.pagination.total,
          has_more: result.pagination.has_more,
          offset,
        });
      } catch (err) {
        setError(turkishApiError(err));
      } finally {
        setLoading(false);
        setRefreshing(false);
        setLoadingMore(false);
      }
    },
    [search, selectedSector, selectedSentiment, selectedRating]
  );

  // Arama ve filtre değişimlerinde debounce
  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => {
      fetchReviews(0, true);
    }, search ? 350 : 0);
    return () => clearTimeout(timer);
  }, [fetchReviews, search, selectedSector, selectedSentiment, selectedRating]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchReviews(0, true);
  };

  const loadMore = () => {
    if (loadingMore || !pagination.has_more) return;
    setLoadingMore(true);
    fetchReviews(pagination.offset + PAGE_SIZE, false);
  };

  const clearFilters = () => {
    setSelectedSector(undefined);
    setSelectedSentiment(undefined);
    setSelectedRating(undefined);
    setSearch('');
  };

  const hasActiveFilters =
    Boolean(selectedSector) ||
    Boolean(selectedSentiment) ||
    Boolean(selectedRating) ||
    search.trim().length > 0;

  return (
    <FlatList
      style={styles.container}
      contentContainerStyle={styles.content}
      data={reviews}
      keyExtractor={(item) => String(item.id)}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.primary} />
      }
      onEndReached={loadMore}
      onEndReachedThreshold={0.4}
      ListHeaderComponent={
        <View style={styles.headerArea}>
          <View style={styles.titleRow}>
            <View>
              <Text style={styles.pageTitle}>Yorumlar</Text>
              <Text style={styles.pageSubtitle}>
                {pagination.total.toLocaleString('tr-TR')} kullanıcı geri bildirimi
              </Text>
            </View>
            {hasActiveFilters && (
              <TouchableOpacity style={styles.clearBtn} onPress={clearFilters}>
                <Ionicons name="close-circle-outline" size={16} color={Colors.negative} />
                <Text style={styles.clearBtnText}>Temizle</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Arama Input */}
          <View style={styles.searchContainer}>
            <Ionicons name="search" size={18} color={Colors.textMuted} style={styles.searchIcon} />
            <TextInput
              style={styles.searchInput}
              placeholder="Yorumlarda anahtar kelime ara..."
              placeholderTextColor={Colors.textMuted}
              value={search}
              onChangeText={setSearch}
            />
            {search.length > 0 && (
              <TouchableOpacity onPress={() => setSearch('')}>
                <Ionicons name="close" size={18} color={Colors.textMuted} />
              </TouchableOpacity>
            )}
          </View>

          {/* Sektör Filtreleri */}
          <Text style={styles.filterSectionTitle}>Sektör</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.chipScroll}
          >
            {SECTOR_FILTERS.map((f) => {
              const isActive = selectedSector === f.id;
              return (
                <TouchableOpacity
                  key={f.label}
                  style={[styles.filterChip, isActive && styles.filterChipActive]}
                  onPress={() => setSelectedSector(f.id)}
                  activeOpacity={0.7}
                >
                  <Text style={[styles.filterChipText, isActive && styles.filterChipTextActive]}>
                    {f.label}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>

          {/* Duygu ve Puan Filtreleri */}
          <View style={styles.dualFilterRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.filterSectionTitle}>Duygu</Text>
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.chipScroll}
              >
                {SENTIMENT_FILTERS.map((f) => {
                  const isActive = selectedSentiment === f.id;
                  return (
                    <TouchableOpacity
                      key={f.label}
                      style={[styles.smallChip, isActive && styles.filterChipActive]}
                      onPress={() => setSelectedSentiment(f.id)}
                      activeOpacity={0.7}
                    >
                      <Text
                        style={[styles.smallChipText, isActive && styles.filterChipTextActive]}
                      >
                        {f.label}
                      </Text>
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            </View>
          </View>

          <View style={{ marginTop: Spacing.sm }}>
            <Text style={styles.filterSectionTitle}>Puan (Yıldız)</Text>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.chipScroll}
            >
              {RATING_FILTERS.map((f) => {
                const isActive = selectedRating === f.id;
                return (
                  <TouchableOpacity
                    key={f.label}
                    style={[styles.ratingChip, isActive && styles.filterChipActive]}
                    onPress={() => setSelectedRating(f.id)}
                    activeOpacity={0.7}
                  >
                    <Text
                      style={[styles.ratingChipText, isActive && styles.filterChipTextActive]}
                    >
                      {f.label}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </ScrollView>
          </View>

          {error ? <Text style={styles.error}>{error}</Text> : null}

          {loading && reviews.length === 0 ? (
            <View style={{ paddingVertical: 40 }}>
              <LoadingSpinner message="Yorumlar filtreleniyor..." />
            </View>
          ) : null}
        </View>
      }
      ListEmptyComponent={
        !loading ? (
          <EmptyState
            message="Seçilen filtrelere uygun yorum bulunamadı."
            icon="chatbubbles-outline"
          />
        ) : null
      }
      renderItem={({ item }) => (
        <ReviewCard review={item} onPress={() => router.push(`/review/${item.id}`)} />
      )}
      ListFooterComponent={
        loadingMore ? (
          <Text style={styles.footer}>Daha fazla yükleniyor...</Text>
        ) : (
          <View style={{ height: 28 }} />
        )
      }
    />
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { padding: Spacing.lg, flexGrow: 1 },
  headerArea: { marginBottom: Spacing.md },
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  pageTitle: {
    fontSize: FontSize.xxxl,
    fontWeight: '800',
    color: Colors.textPrimary,
  },
  pageSubtitle: {
    fontSize: FontSize.md,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  clearBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: 'rgba(255, 82, 82, 0.12)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: BorderRadius.sm,
  },
  clearBtnText: {
    color: Colors.negative,
    fontSize: FontSize.xs,
    fontWeight: '700',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: Spacing.md,
    marginTop: Spacing.sm,
    marginBottom: Spacing.md,
  },
  searchIcon: { marginRight: Spacing.sm },
  searchInput: {
    flex: 1,
    color: Colors.textPrimary,
    paddingVertical: 12,
    fontSize: FontSize.md,
  },
  filterSectionTitle: {
    color: Colors.textMuted,
    fontSize: FontSize.xs,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  chipScroll: {
    flexDirection: 'row',
    gap: Spacing.sm,
    paddingBottom: Spacing.sm,
  },
  filterChip: {
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  filterChipActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primaryLight,
  },
  filterChipText: {
    color: Colors.textSecondary,
    fontSize: FontSize.sm,
    fontWeight: '600',
  },
  filterChipTextActive: {
    color: Colors.white,
    fontWeight: '700',
  },
  dualFilterRow: {
    marginTop: Spacing.xs,
  },
  smallChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  smallChipText: {
    color: Colors.textSecondary,
    fontSize: FontSize.xs,
    fontWeight: '600',
  },
  ratingChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: BorderRadius.sm,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  ratingChipText: {
    color: Colors.star,
    fontSize: FontSize.xs,
    fontWeight: '700',
  },
  error: {
    color: Colors.negative,
    marginVertical: Spacing.sm,
  },
  footer: {
    color: Colors.textMuted,
    textAlign: 'center',
    paddingVertical: Spacing.md,
    fontSize: FontSize.xs,
  },
});
