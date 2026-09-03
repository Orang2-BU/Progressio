import 'package:flutter/material.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_spacing.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';
import 'package:progressio_mobile/core/constants/cute_iconify_icons.dart';
import 'package:progressio_mobile/presentation/pages/auth/login/widgets/animated_text_field.dart';
import 'package:progressio_mobile/presentation/pages/auth/login/widgets/mascot_banner.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  bool _rememberMe = true;
  bool _obscurePassword = true;
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _handleLogin() {
    if (_formKey.currentState?.validate() ?? false) {
      setState(() => _isLoading = true);
      Future.delayed(const Duration(seconds: 1), () {
        if (mounted) {
          setState(() => _isLoading = false);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              backgroundColor: AppColors.darkSlate,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppRadius.lg),
              ),
              content: Row(
                children: const [
                  Text('🔥', style: TextStyle(fontSize: 18)),
                  SizedBox(width: 8),
                  Text(
                    'Login Berhasil! Selamat datang di Progressio.',
                    style: TextStyle(
                      fontFamily: AppTypography.headlineFont,
                      fontWeight: FontWeight.w600,
                      color: AppColors.limePrimary,
                    ),
                  ),
                ],
              ),
            ),
          );
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.canvasBg,
      body: Stack(
        children: [
          // Background Gradient Soft Lime di bagian atas sesuai Dopamine Style
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            height: 340,
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Color(0xFFE9F8CC),
                    Color(0xFFF3FCE5),
                    AppColors.canvasBg,
                  ],
                  stops: [0.0, 0.65, 1.0],
                ),
              ),
            ),
          ),

          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xl),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: AppSpacing.sm),

                    // Top Bar: Logo & Brand + Tag Version "v2.4 NEO"
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // Logo Circle & Brand Name
                        Row(
                          children: [
                            Container(
                              width: 38,
                              height: 38,
                              decoration: const BoxDecoration(
                                shape: BoxShape.circle,
                                color: AppColors.darkSlate,
                              ),
                              child: Center(
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: const [
                                    Text(
                                      'P',
                                      style: TextStyle(
                                        fontFamily: AppTypography.headlineFont,
                                        fontSize: 18,
                                        fontWeight: FontWeight.w900,
                                        color: AppColors.limePrimary,
                                      ),
                                    ),
                                    Text(
                                      '⚡',
                                      style: TextStyle(fontSize: 10),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            const SizedBox(width: AppSpacing.sm),
                            const Text(
                              'PROGRESSIO',
                              style: TextStyle(
                                fontFamily: AppTypography.headlineFont,
                                fontSize: 16,
                                fontWeight: FontWeight.w900,
                                letterSpacing: 0.8,
                                color: AppColors.darkSlate,
                              ),
                            ),
                          ],
                        ),

                        // Version Capsule Tag (V2.4 NEO)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 5,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(AppRadius.pill),
                            border: Border.all(
                              color: AppColors.borderColor,
                              width: 1.2,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.03),
                                blurRadius: 4,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Container(
                                width: 7,
                                height: 7,
                                decoration: const BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: Color(0xFF8CE323),
                                ),
                              ),
                              const SizedBox(width: 5),
                              const Text(
                                'V2.4 NEO',
                                style: TextStyle(
                                  fontFamily: AppTypography.headlineFont,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w800,
                                  color: AppColors.darkSlate,
                                  letterSpacing: 0.4,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 28),

                    // Mascot Banner + Streak Capsule
                    const MascotBanner(),

                    const SizedBox(height: 24),

                    // Headline "Selamat Datang! 👋"
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: const [
                        Text(
                          'Selamat Datang!',
                          style: TextStyle(
                            fontFamily: AppTypography.headlineFont,
                            fontSize: 24,
                            fontWeight: FontWeight.w800,
                            color: AppColors.textMain,
                          ),
                        ),
                        SizedBox(width: 6),
                        Text(
                          '👋',
                          style: TextStyle(fontSize: 22),
                        ),
                      ],
                    ),

                    const SizedBox(height: 8),

                    // Subtitle
                    const Text(
                      'Masuk untuk melanjutkan streak dan\npetualangan ngodingmu',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontFamily: AppTypography.bodyFont,
                        fontSize: 13,
                        color: AppColors.textMuted,
                        height: 1.45,
                      ),
                    ),

                    const SizedBox(height: 28),

                    // Email Belajar Field with Dopamine animation & Cute Iconify Icon
                    AnimatedDopamineTextField(
                      controller: _emailController,
                      label: 'Email Belajar',
                      hintText: 'Masukkan email kamu',
                      iconifySvg: CuteIconifyIcons.emailCute,
                      activeColor: AppColors.lavenderPrimary,
                      keyboardType: TextInputType.emailAddress,
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Email wajib diisi';
                        }
                        if (!value.contains('@')) {
                          return 'Format email tidak valid';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 18),

                    // Kata Sandi Field with Dopamine animation & Cute Iconify Icon
                    AnimatedDopamineTextField(
                      controller: _passwordController,
                      label: 'Kata Sandi',
                      hintText: 'Masukkan kata sandi',
                      iconifySvg: CuteIconifyIcons.lockCute,
                      activeColor: AppColors.limeDeep,
                      isPassword: true,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Kata sandi wajib diisi';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 14),

                    // Row: Ingat Saya & Lupa Password
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // Checkbox: Ingat Saya
                        GestureDetector(
                          onTap: () {
                            setState(() {
                              _rememberMe = !_rememberMe;
                            });
                          },
                          child: Row(
                            children: [
                              Container(
                                width: 20,
                                height: 20,
                                decoration: BoxDecoration(
                                  color: _rememberMe
                                      ? const Color(0xFF8CE323)
                                      : Colors.white,
                                  borderRadius: BorderRadius.circular(6),
                                  border: Border.all(
                                    color: _rememberMe
                                        ? const Color(0xFF8CE323)
                                        : AppColors.borderColor,
                                    width: 1.5,
                                  ),
                                ),
                                child: _rememberMe
                                    ? const Icon(
                                        Icons.check,
                                        size: 14,
                                        color: Colors.white,
                                      )
                                    : null,
                              ),
                              const SizedBox(width: 8),
                              const Text(
                                'Ingat Saya',
                                style: TextStyle(
                                  fontFamily: AppTypography.bodyFont,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: AppColors.textMain,
                                ),
                              ),
                            ],
                          ),
                        ),

                        // Link: Lupa Password?
                        GestureDetector(
                          onTap: () {},
                          child: const Text(
                            'Lupa Password?',
                            style: TextStyle(
                              fontFamily: AppTypography.headlineFont,
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              color: AppColors.lavenderPrimary,
                            ),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // Tombol CTA: Masuk Sekarang (Lime Glow Pill)
                    Container(
                      height: 52,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(AppRadius.pill),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFFB5F942).withOpacity(0.55),
                            blurRadius: 16,
                            offset: const Offset(0, 6),
                          ),
                        ],
                      ),
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : _handleLogin,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFB8F846),
                          foregroundColor: AppColors.darkSlate,
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(AppRadius.pill),
                          ),
                        ),
                        child: _isLoading
                            ? const SizedBox(
                                width: 22,
                                height: 22,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                  color: AppColors.darkSlate,
                                ),
                              )
                            : Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: const [
                                  Text(
                                    'Masuk Sekarang',
                                    style: TextStyle(
                                      fontFamily: AppTypography.headlineFont,
                                      fontSize: 15,
                                      fontWeight: FontWeight.w800,
                                      color: AppColors.darkSlate,
                                    ),
                                  ),
                                  SizedBox(width: 8),
                                  Icon(
                                    Icons.arrow_forward_rounded,
                                    size: 18,
                                    color: AppColors.darkSlate,
                                  ),
                                ],
                              ),
                      ),
                    ),

                    const SizedBox(height: 20),

                    // Divider: "ATAU" Pill Divider
                    Row(
                      children: [
                        const Expanded(
                          child: Divider(
                            color: Color(0xFFE5EBE0),
                            thickness: 1,
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 10),
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 3,
                            ),
                            decoration: BoxDecoration(
                              color: const Color(0xFFEFF5EA),
                              borderRadius: BorderRadius.circular(AppRadius.pill),
                            ),
                            child: const Text(
                              'ATAU',
                              style: TextStyle(
                                fontFamily: AppTypography.headlineFont,
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                color: AppColors.textMuted,
                                letterSpacing: 0.6,
                              ),
                            ),
                          ),
                        ),
                        const Expanded(
                          child: Divider(
                            color: Color(0xFFE5EBE0),
                            thickness: 1,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 20),

                    // Tombol: Lanjutkan dengan Google
                    Container(
                      height: 52,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(AppRadius.pill),
                        border: Border.all(
                          color: const Color(0xFFE5EBE0),
                          width: 1.2,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.02),
                            blurRadius: 6,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Material(
                        color: Colors.transparent,
                        child: InkWell(
                          borderRadius: BorderRadius.circular(AppRadius.pill),
                          onTap: () {},
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              // Ikon Google 'G' Multi-Color Minimalis
                              SizedBox(
                                width: 20,
                                height: 20,
                                child: Stack(
                                  alignment: Alignment.center,
                                  children: const [
                                    Text(
                                      'G',
                                      style: TextStyle(
                                        fontFamily: AppTypography.headlineFont,
                                        fontSize: 16,
                                        fontWeight: FontWeight.w900,
                                        color: Color(0xFFEA4335),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(width: 10),
                              const Text(
                                'Lanjutkan dengan Google',
                                style: TextStyle(
                                  fontFamily: AppTypography.headlineFont,
                                  fontSize: 14,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.darkSlate,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 28),

                    // Footer: Belum punya akun Progressio? Daftar Gratis
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          'Belum punya akun Progressio? ',
                          style: TextStyle(
                            fontFamily: AppTypography.bodyFont,
                            fontSize: 12,
                            color: AppColors.textMuted,
                          ),
                        ),
                        GestureDetector(
                          onTap: () {},
                          child: const Text(
                            'Daftar Gratis',
                            style: TextStyle(
                              fontFamily: AppTypography.headlineFont,
                              fontSize: 12,
                              fontWeight: FontWeight.w800,
                              color: AppColors.lavenderPrimary,
                            ),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 36),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
