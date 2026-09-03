import 'package:flutter/material.dart';
import 'package:iconify_flutter/iconify_flutter.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_spacing.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';
import 'package:progressio_mobile/core/constants/cute_iconify_icons.dart';
import 'package:progressio_mobile/presentation/pages/auth/login/widgets/animated_text_field.dart';
import 'package:progressio_mobile/presentation/pages/auth/login/widgets/fluid_checkbox.dart';
import 'package:progressio_mobile/presentation/pages/auth/register/register_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  late final AnimationController _animController;
  late final Animation<Offset> _slideAnimation;
  late final Animation<double> _fadeAnimation;

  bool _isRegisterMode = false;
  bool _rememberMe = true;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 750),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0.0, 0.22),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _animController,
        curve: Curves.easeOutCubic,
      ),
    );

    _fadeAnimation = CurvedAnimation(
      parent: _animController,
      curve: const Interval(0.0, 0.8, curve: Curves.easeOut),
    );

    _animController.forward();
  }

  @override
  void dispose() {
    _animController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _scrollController.dispose();
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
      backgroundColor: Colors.white,
      body: LayoutBuilder(
        builder: (context, constraints) {
          final screenHeight = constraints.maxHeight;

          return Stack(
            children: [
              // Header Image Lime with Gradient (Tetap statis tanpa zoom/resize saat ganti form)
              Positioned(
                top: -20,
                left: 0,
                right: 0,
                height: 480,
                child: Container(
                  decoration: const BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Color(0xFFC7F37A), // Hijau lime di atas
                        Color(0xFFE8FCD0), // Transisi lembut
                        Colors.white,      // Putih di bawah
                      ],
                      stops: [0.0, 0.65, 1.0],
                    ),
                  ),
                  child: SafeArea(
                    bottom: false,
                    child: Center(
                      child: Builder(
                        builder: (context) {
                          final dpr = MediaQuery.of(context).devicePixelRatio;
                          const baseSize = 480.0;
                          final physicalSize = (baseSize * dpr).toInt();
                          return Image(
                            image: ResizeImage(
                              const AssetImage('assets/images/Hello_Login.png'),
                              width: physicalSize,
                              height: physicalSize,
                            ),
                            width: baseSize,
                            height: baseSize,
                            fit: BoxFit.contain,
                            filterQuality: FilterQuality.high,
                            isAntiAlias: true,
                          );
                        },
                      ),
                    ),
                  ),
                ),
              ),

              // Scrollable Content
              Positioned.fill(
                child: SingleChildScrollView(
                  controller: _scrollController,
                  child: ConstrainedBox(
                    constraints: BoxConstraints(
                      minHeight: screenHeight,
                    ),
                    child: IntrinsicHeight(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          // Spacer dinamis di atas — menyesuaikan ukuran layar agar card selalu pas di bawah
                          const SizedBox(height: 24),
                          const Spacer(),

                          // Bottom Card Sheet Putih menempel pas di bawah (tanpa geser saat ganti form)
                          SlideTransition(
                            position: _slideAnimation,
                            child: FadeTransition(
                              opacity: _fadeAnimation,
                              child: Container(
                                width: double.infinity,
                                clipBehavior: Clip.antiAlias,
                                decoration: const BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.vertical(
                                    top: Radius.circular(32),
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Color(0x18000000),
                                      blurRadius: 24,
                                      offset: Offset(0, -5),
                                    ),
                                  ],
                                ),
                                padding: const EdgeInsets.fromLTRB(
                                  26,
                                  16,
                                  26,
                                  32,
                                ),
                                child: AnimatedSize(
                                  duration: const Duration(milliseconds: 400),
                                  curve: Curves.easeOutCubic,
                                  alignment: Alignment.topCenter,
                                  child: AnimatedSwitcher(
                                    duration: const Duration(milliseconds: 380),
                                    switchInCurve: Curves.easeOutCubic,
                                    switchOutCurve: Curves.easeInCubic,
                                    layoutBuilder: (Widget? currentChild, List<Widget> previousChildren) {
                                      return Stack(
                                        alignment: Alignment.topCenter,
                                        children: <Widget>[
                                          ...previousChildren,
                                          ?currentChild,
                                        ],
                                      );
                                    },
                                    transitionBuilder: (Widget child, Animation<double> animation) {
                                      final isChildRegister = child.key == const ValueKey<String>('register_form');
                                      final beginOffset = isChildRegister
                                          ? const Offset(0.30, 0.0)
                                          : const Offset(-0.30, 0.0);
                                      
                                      // Animasi berurutan (sequential) agar tidak tumpang tindih:
                                      // Form lama keluar dulu, form baru masuk bergantian secara rapi.
                                      final seqAnimation = CurvedAnimation(
                                        parent: animation,
                                        curve: const Interval(0.42, 1.0, curve: Curves.easeOutCubic),
                                      );

                                      return FadeTransition(
                                        opacity: seqAnimation,
                                        child: SlideTransition(
                                          position: Tween<Offset>(
                                            begin: beginOffset,
                                            end: Offset.zero,
                                          ).animate(seqAnimation),
                                          child: Container(
                                            color: Colors.white,
                                            child: child,
                                          ),
                                        ),
                                      );
                                    },
                                    child: _isRegisterMode
                                        ? KeyedSubtree(
                                            key: const ValueKey<String>('register_form'),
                                            child: RegisterFormContent(
                                              onSwitchToLogin: () {
                                                setState(() {
                                                  _isRegisterMode = false;
                                                });
                                                if (_scrollController.hasClients) {
                                                  _scrollController.animateTo(
                                                    0,
                                                    duration: const Duration(milliseconds: 300),
                                                    curve: Curves.easeOut,
                                                  );
                                                }
                                              },
                                            ),
                                          )
                                        : KeyedSubtree(
                                            key: const ValueKey<String>('login_form'),
                                            child: _buildLoginForm(context),
                                          ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildLoginForm(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Handle Pill Bar (Garis horizontal abu-abu kecil di atas card)
          Center(
            child: Container(
              width: 44,
              height: 4.5,
              decoration: BoxDecoration(
                color: const Color(0xFFE2E8DE),
                borderRadius: BorderRadius.circular(3),
              ),
            ),
          ),
          const SizedBox(height: 22),

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
              SizedBox(width: 8),
              Text(
                '👋',
                style: TextStyle(fontSize: 22),
              ),
            ],
          ),
          const SizedBox(height: 6),
          const Text(
            'Masuk untuk melanjutkan',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: AppTypography.bodyFont,
              fontSize: 13,
              color: AppColors.textMuted,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 28),
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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              FluidDopamineCheckbox(
                value: _rememberMe,
                label: 'Ingat Saya',
                activeColor: const Color(0xFF8CE323),
                onChanged: (newValue) {
                  setState(() {
                    _rememberMe = newValue;
                  });
                },
              ),
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
                            letterSpacing: 0.2,
                          ),
                        ),
                        SizedBox(width: 8),
                        Icon(
                          Icons.arrow_forward_rounded,
                          size: 19,
                          color: AppColors.darkSlate,
                        ),
                      ],
                    ),
            ),
          ),

          const SizedBox(height: 24),

          // Divider: "── ATAU ──"
          Row(
            children: [
              Expanded(
                child: Container(
                  height: 1,
                  color: const Color(0xFFE5EBE0),
                ),
              ),
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 14),
                child: Text(
                  'ATAU',
                  style: TextStyle(
                    fontFamily: AppTypography.headlineFont,
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textMuted,
                    letterSpacing: 0.8,
                  ),
                ),
              ),
              Expanded(
                child: Container(
                  height: 1,
                  color: const Color(0xFFE5EBE0),
                ),
              ),
            ],
          ),

          const SizedBox(height: 20),

          // Tombol Google
          Container(
            height: 52,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(AppRadius.pill),
              border: Border.all(
                color: const Color(0xFFE2E8DE),
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
                  children: const [
                    Iconify(
                      CuteIconifyIcons.googleLogo,
                      size: 20,
                    ),
                    SizedBox(width: 12),
                    Text(
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
          Wrap(
            alignment: WrapAlignment.center,
            crossAxisAlignment: WrapCrossAlignment.center,
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
                onTap: () {
                  setState(() {
                    _isRegisterMode = true;
                  });
                  if (_scrollController.hasClients) {
                    _scrollController.animateTo(
                      0,
                      duration: const Duration(milliseconds: 300),
                      curve: Curves.easeOut,
                    );
                  }
                },
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
    );
  }
}
