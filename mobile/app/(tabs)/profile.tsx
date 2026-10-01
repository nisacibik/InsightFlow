import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, BorderRadius, Spacing } from '../../constants/theme';
import { useAuth } from '../../contexts/AuthContext';
import api, { turkishApiError } from '../../services/api';

const SUBSECTOR_OPTIONS = ['SaaS', 'Yapay Zekâ', 'Mobil Uygulamalar'];
const BUSINESS_MODEL_OPTIONS = ['B2B', 'B2C', 'B2B2C', 'Marketplace'];
const PRODUCT_STAGE_OPTIONS = ['Idea', 'MVP', 'Growth', 'Mature'];

export default function ProfileScreen() {
  const router = useRouter();
  const { user, logout } = useAuth();

  const [company, setCompany] = useState<any>(null);
  const [loadingCompany, setLoadingCompany] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const [companyName, setCompanyName] = useState('');
  const [subsector, setSubsector] = useState('');
  const [productArea, setProductArea] = useState('');
  const [businessModel, setBusinessModel] = useState('');
  const [productStage, setProductStage] = useState('');
  const [description, setDescription] = useState('');

  const fetchCompany = useCallback(async () => {
    try {
      const res = await api.getMyCompany();
      const c = res?.company || null;
      setCompany(c);
      if (c) {
        setCompanyName(c.company_name || '');
        setSubsector(c.subsector || '');
        setProductArea(c.product_area || '');
        setBusinessModel(c.business_model || '');
        setProductStage(c.product_stage || '');
        setDescription(c.description || '');
      }
    } catch {
      setCompany(null);
    } finally {
      setLoadingCompany(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchCompany();
  }, [fetchCompany]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchCompany();
  };

  const onSave = async () => {
    if (!companyName.trim()) {
      setError('Şirket adı zorunludur.');
      return;
    }
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const data = {
        company_name: companyName.trim(),
        sector: 'Bilişim',
        subsector: subsector || null,
        product_area: productArea.trim() || null,
        business_model: businessModel || null,
        product_stage: productStage || null,
        description: description.trim() || null,
      };

      if (company) {
        const updated = await api.updateCompany(data);
        setCompany(updated);
      } else {
        const created = await api.createCompany(data);
        setCompany(created);
      }
      setEditing(false);
      setSuccess('Şirket bilgileri kaydedildi.');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(turkishApiError(err, 'Şirket bilgileri kaydedilemedi.'));
    } finally {
      setSaving(false);
    }
  };

  const onLogout = async () => {
    await logout();
    router.replace('/login');
  };

  const renderPicker = (
    label: string,
    options: string[],
    selected: string,
    onSelect: (v: string) => void
  ) => (
    <View style={styles.fieldGroup}>
      <Text style={styles.label}>{label}</Text>
      {editing ? (
        <View style={styles.chipRow}>
          {options.map((opt) => (
            <TouchableOpacity
              key={opt}
              style={[styles.chip, selected === opt && styles.chipActive]}
              onPress={() => onSelect(selected === opt ? '' : opt)}
            >
              <Text style={[styles.chipText, selected === opt && styles.chipTextActive]}>
                {opt}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      ) : (
        <Text style={styles.value}>{selected || '—'}</Text>
      )}
    </View>
  );

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.primary} />}
    >
      <Text style={styles.title}>Profil</Text>

      <View style={styles.card}>
        <View style={styles.avatarRow}>
          <View style={styles.avatar}>
            <Ionicons name="person" size={28} color={Colors.primary} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.emailText}>{user?.email}</Text>
            <Text style={styles.roleText}>Kullanıcı</Text>
          </View>
        </View>
      </View>

      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Şirket Bilgileri</Text>
        {!loadingCompany && (
          <TouchableOpacity onPress={() => { setEditing(!editing); setError(null); setSuccess(null); }}>
            <Ionicons name={editing ? 'close' : 'create-outline'} size={22} color={Colors.primary} />
          </TouchableOpacity>
        )}
      </View>

      {loadingCompany ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator color={Colors.primary} />
        </View>
      ) : (
        <View style={styles.card}>
          <View style={styles.fieldGroup}>
            <Text style={styles.label}>Şirket Adı</Text>
            {editing ? (
              <TextInput
                style={styles.input}
                value={companyName}
                onChangeText={(t) => { setCompanyName(t); setError(null); }}
                placeholder="Şirket adı"
                placeholderTextColor={Colors.textMuted}
              />
            ) : (
              <Text style={styles.value}>{company?.company_name || '—'}</Text>
            )}
          </View>

          <View style={styles.fieldGroup}>
            <Text style={styles.label}>Sektör</Text>
            <Text style={styles.value}>{company?.sector || 'Bilişim'}</Text>
          </View>

          {renderPicker('Alt Sektör', SUBSECTOR_OPTIONS, subsector, setSubsector)}
          {renderPicker('İş Modeli', BUSINESS_MODEL_OPTIONS, businessModel, setBusinessModel)}
          {renderPicker('Ürün Aşaması', PRODUCT_STAGE_OPTIONS, productStage, setProductStage)}

          <View style={styles.fieldGroup}>
            <Text style={styles.label}>Ürün Alanı</Text>
            {editing ? (
              <TextInput
                style={styles.input}
                value={productArea}
                onChangeText={setProductArea}
                placeholder="Örn: CRM, E-ticaret"
                placeholderTextColor={Colors.textMuted}
              />
            ) : (
              <Text style={styles.value}>{company?.product_area || '—'}</Text>
            )}
          </View>

          <View style={styles.fieldGroup}>
            <Text style={styles.label}>Açıklama</Text>
            {editing ? (
              <TextInput
                style={[styles.input, styles.textarea]}
                value={description}
                onChangeText={setDescription}
                placeholder="Şirket açıklaması"
                placeholderTextColor={Colors.textMuted}
                multiline
                numberOfLines={3}
                textAlignVertical="top"
              />
            ) : (
              <Text style={styles.value}>{company?.description || '—'}</Text>
            )}
          </View>

          {error ? <Text style={styles.error}>{error}</Text> : null}
          {success ? <Text style={styles.success}>{success}</Text> : null}

          {editing && (
            <TouchableOpacity style={styles.saveButton} onPress={onSave} disabled={saving}>
              <Text style={styles.saveButtonText}>{saving ? 'Kaydediliyor...' : 'Kaydet'}</Text>
            </TouchableOpacity>
          )}
        </View>
      )}

      <TouchableOpacity style={styles.logoutButton} onPress={onLogout}>
        <Ionicons name="log-out-outline" size={20} color={Colors.white} />
        <Text style={styles.logoutText}>Çıkış Yap</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  contentContainer: {
    padding: Spacing.lg,
    paddingBottom: 40,
  },
  title: {
    fontSize: FontSize.xxxl,
    fontWeight: '800',
    color: Colors.textPrimary,
    marginBottom: Spacing.xl,
  },
  card: {
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.md,
  },
  avatarRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
  },
  avatar: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: `${Colors.primary}20`,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emailText: {
    color: Colors.textPrimary,
    fontSize: FontSize.lg,
    fontWeight: '600',
  },
  roleText: {
    color: Colors.textMuted,
    fontSize: FontSize.sm,
    marginTop: 2,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
    marginTop: Spacing.md,
  },
  sectionTitle: {
    fontSize: FontSize.xl,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  loadingContainer: {
    paddingVertical: Spacing.xxl,
    alignItems: 'center',
  },
  fieldGroup: {
    marginBottom: Spacing.md,
  },
  label: {
    color: Colors.textMuted,
    fontSize: FontSize.sm,
    fontWeight: '600',
    marginBottom: 4,
  },
  value: {
    color: Colors.textPrimary,
    fontSize: FontSize.md,
    fontWeight: '500',
  },
  input: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    color: Colors.textPrimary,
    paddingHorizontal: Spacing.md,
    paddingVertical: 10,
    fontSize: FontSize.md,
  },
  textarea: {
    minHeight: 70,
    paddingTop: 10,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  chipActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  chipText: {
    color: Colors.textSecondary,
    fontSize: FontSize.sm,
    fontWeight: '600',
  },
  chipTextActive: {
    color: Colors.white,
  },
  saveButton: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.md,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: Spacing.sm,
  },
  saveButtonText: {
    color: Colors.white,
    fontWeight: '700',
    fontSize: FontSize.md,
  },
  error: {
    color: Colors.negative,
    textAlign: 'center',
    marginTop: Spacing.sm,
  },
  success: {
    color: Colors.positive,
    textAlign: 'center',
    marginTop: Spacing.sm,
  },
  logoutButton: {
    flexDirection: 'row',
    backgroundColor: Colors.negative,
    borderRadius: BorderRadius.md,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: Spacing.lg,
    gap: 8,
  },
  logoutText: {
    color: Colors.white,
    fontWeight: '700',
    fontSize: FontSize.lg,
  },
});
