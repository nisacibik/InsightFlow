import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Colors, FontSize, BorderRadius, Spacing } from '../constants/theme';
import api, { turkishApiError } from '../services/api';

const SUBSECTOR_OPTIONS = ['SaaS', 'Yapay Zekâ', 'Mobil Uygulamalar'];
const BUSINESS_MODEL_OPTIONS = ['B2B', 'B2C', 'B2B2C', 'Marketplace'];
const PRODUCT_STAGE_OPTIONS = ['Idea', 'MVP', 'Growth', 'Mature'];

export default function CompanySetupScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [companyName, setCompanyName] = useState('');
  const [subsector, setSubsector] = useState('');
  const [productArea, setProductArea] = useState('');
  const [businessModel, setBusinessModel] = useState('');
  const [productStage, setProductStage] = useState('');
  const [description, setDescription] = useState('');

  const onSubmit = async () => {
    if (!companyName.trim()) {
      setError('Şirket adı zorunludur.');
      return;
    }
    if (!subsector) {
      setError('Alt sektör seçimi zorunludur.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await api.createCompany({
        company_name: companyName.trim(),
        sector: 'Bilişim',
        subsector,
        product_area: productArea.trim() || null,
        business_model: businessModel || null,
        product_stage: productStage || null,
        description: description.trim() || null,
      });
      router.replace('/(tabs)');
    } catch (err) {
      setError(turkishApiError(err, 'Şirket bilgileri kaydedilemedi.'));
    } finally {
      setLoading(false);
    }
  };

  const renderPicker = (
    label: string,
    options: string[],
    selected: string,
    onSelect: (v: string) => void
  ) => (
    <View style={styles.pickerSection}>
      <Text style={styles.label}>{label}</Text>
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
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Şirket Bilgileri</Text>
        <Text style={styles.subtitle}>Kayıt işlemini tamamlamak için şirket bilgilerinizi girin</Text>

        <Text style={styles.label}>Şirket Adı *</Text>
        <TextInput
          style={styles.input}
          placeholder="Şirket adını girin"
          placeholderTextColor={Colors.textMuted}
          value={companyName}
          onChangeText={(t) => { setCompanyName(t); setError(null); }}
        />

        <Text style={styles.label}>Sektör</Text>
        <View style={styles.fixedField}>
          <Text style={styles.fixedText}>Bilişim</Text>
        </View>

        {renderPicker('Alt Sektör *', SUBSECTOR_OPTIONS, subsector, setSubsector)}
        {renderPicker('İş Modeli', BUSINESS_MODEL_OPTIONS, businessModel, setBusinessModel)}
        {renderPicker('Ürün Aşaması', PRODUCT_STAGE_OPTIONS, productStage, setProductStage)}

        <Text style={styles.label}>Ürün Alanı</Text>
        <TextInput
          style={styles.input}
          placeholder="Örn: CRM, E-ticaret, Analitik"
          placeholderTextColor={Colors.textMuted}
          value={productArea}
          onChangeText={setProductArea}
        />

        <Text style={styles.label}>Şirket Açıklaması</Text>
        <TextInput
          style={[styles.input, styles.textarea]}
          placeholder="Şirketinizi kısaca tanımlayın"
          placeholderTextColor={Colors.textMuted}
          multiline
          numberOfLines={3}
          textAlignVertical="top"
          value={description}
          onChangeText={setDescription}
        />

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <TouchableOpacity style={styles.button} onPress={onSubmit} disabled={loading}>
          <Text style={styles.buttonText}>{loading ? 'Kaydediliyor...' : 'Tamamla'}</Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={() => router.replace('/(tabs)')}>
          <Text style={styles.skip}>Şimdilik atla</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: Colors.background },
  content: {
    flexGrow: 1,
    padding: Spacing.xxl,
    paddingTop: Spacing.xl,
  },
  title: {
    fontSize: FontSize.xxxl,
    fontWeight: '800',
    color: Colors.textPrimary,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: FontSize.md,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginBottom: Spacing.xl,
    marginTop: Spacing.sm,
  },
  label: {
    color: Colors.textSecondary,
    fontSize: FontSize.sm,
    fontWeight: '600',
    marginBottom: 6,
    marginTop: Spacing.md,
  },
  input: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    color: Colors.textPrimary,
    paddingHorizontal: Spacing.lg,
    paddingVertical: 14,
    fontSize: FontSize.md,
  },
  textarea: {
    minHeight: 80,
    paddingTop: 14,
  },
  fixedField: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: Spacing.lg,
    paddingVertical: 14,
    opacity: 0.7,
  },
  fixedText: {
    color: Colors.textPrimary,
    fontSize: FontSize.md,
  },
  pickerSection: {
    marginTop: Spacing.md,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    paddingHorizontal: 16,
    paddingVertical: 10,
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
  button: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.md,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: Spacing.xl,
  },
  buttonText: {
    color: Colors.white,
    fontWeight: '700',
    fontSize: FontSize.lg,
  },
  error: {
    color: Colors.negative,
    textAlign: 'center',
    marginTop: Spacing.md,
  },
  skip: {
    color: Colors.textMuted,
    textAlign: 'center',
    marginTop: Spacing.lg,
    fontSize: FontSize.md,
  },
});
