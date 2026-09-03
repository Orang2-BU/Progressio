import 'package:flutter/material.dart';
import 'package:iconify_flutter/iconify_flutter.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_spacing.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';
import 'package:progressio_mobile/core/constants/cute_iconify_icons.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// AnimatedDopamineTextField — Input pill dengan interaksi & animasi Dopamine
/// ─────────────────────────────────────────────────────────────────────────────
class AnimatedDopamineTextField extends StatefulWidget {
  final TextEditingController controller;
  final String label;
  final String hintText;
  final String? iconifySvg;
  final IconData? prefixIcon;
  final Color activeColor;
  final bool isPassword;
  final TextInputType keyboardType;
  final String? Function(String?)? validator;

  const AnimatedDopamineTextField({
    super.key,
    required this.controller,
    required this.label,
    required this.hintText,
    this.iconifySvg,
    this.prefixIcon,
    this.activeColor = AppColors.limeDeep,
    this.isPassword = false,
    this.keyboardType = TextInputType.text,
    this.validator,
  });

  @override
  State<AnimatedDopamineTextField> createState() => _AnimatedDopamineTextFieldState();
}

class _AnimatedDopamineTextFieldState extends State<AnimatedDopamineTextField> {
  final FocusNode _focusNode = FocusNode();
  bool _isFocused = false;
  bool _obscureText = true;

  @override
  void initState() {
    super.initState();
    _focusNode.addListener(() {
      setState(() {
        _isFocused = _focusNode.hasFocus;
      });
    });
  }

  @override
  void dispose() {
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Label dengan animasi perubahan warna saat fokus
        AnimatedDefaultTextStyle(
          duration: const Duration(milliseconds: 200),
          style: TextStyle(
            fontFamily: AppTypography.headlineFont,
            fontSize: 13,
            fontWeight: FontWeight.w700,
            color: _isFocused ? AppColors.darkSlate : AppColors.textMain,
          ),
          child: Row(
            children: [
              Text(widget.label),
              if (_isFocused) ...[
                const SizedBox(width: 6),
                Container(
                  width: 5,
                  height: 5,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: widget.activeColor,
                  ),
                ),
              ],
            ],
          ),
        ),
        const SizedBox(height: 8),

        // Input Container dengan Micro-Scale & Dynamic Glow Shadow
        AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOutCubic,
          transform: Matrix4.identity()..scale(_isFocused ? 1.018 : 1.0),
          transformAlignment: Alignment.center,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(AppRadius.pill),
            color: Colors.white,
            boxShadow: _isFocused
                ? [
                    BoxShadow(
                      color: widget.activeColor.withOpacity(0.32),
                      blurRadius: 18,
                      offset: const Offset(0, 6),
                    ),
                    BoxShadow(
                      color: Colors.black.withOpacity(0.04),
                      blurRadius: 6,
                      offset: const Offset(0, 2),
                    ),
                  ]
                : [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.02),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
          ),
          child: TextFormField(
            controller: widget.controller,
            focusNode: _focusNode,
            keyboardType: widget.keyboardType,
            obscureText: widget.isPassword ? _obscureText : false,
            validator: widget.validator,
            style: const TextStyle(
              fontFamily: AppTypography.bodyFont,
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: AppColors.textMain,
            ),
            decoration: InputDecoration(
              hintText: widget.hintText,
              hintStyle: const TextStyle(
                color: AppColors.textMuted,
                fontSize: 13,
              ),
              prefixIcon: Padding(
                padding: const EdgeInsets.only(left: 18, right: 12),
                child: AnimatedScale(
                  scale: _isFocused ? 1.18 : 1.0,
                  duration: const Duration(milliseconds: 200),
                  curve: Curves.easeOutBack,
                  child: widget.iconifySvg != null
                      ? Iconify(
                          widget.iconifySvg!,
                          color: _isFocused ? widget.activeColor : AppColors.textMuted,
                          size: 21,
                        )
                      : Icon(
                          widget.prefixIcon ?? Icons.star,
                          color: _isFocused ? widget.activeColor : AppColors.textMuted,
                          size: 20,
                        ),
                ),
              ),
              prefixIconConstraints: const BoxConstraints(
                minWidth: 48,
                minHeight: 24,
              ),
              suffixIcon: widget.isPassword
                  ? Padding(
                      padding: const EdgeInsets.only(right: 6),
                      child: IconButton(
                        iconSize: 22,
                        splashRadius: 20,
                        constraints: const BoxConstraints(
                          minWidth: 40,
                          minHeight: 40,
                        ),
                        style: IconButton.styleFrom(
                          shape: const CircleBorder(),
                          hoverColor: Colors.black.withOpacity(0.06),
                          highlightColor: Colors.black.withOpacity(0.08),
                        ),
                        icon: AnimatedSwitcher(
                          duration: const Duration(milliseconds: 200),
                          transitionBuilder: (child, anim) => ScaleTransition(scale: anim, child: child),
                          child: _obscureText
                              ? Iconify(
                                  CuteIconifyIcons.eyeCute,
                                  key: const ValueKey<bool>(true),
                                  color: _isFocused ? AppColors.darkSlate : AppColors.textMuted,
                                  size: 20,
                                )
                              : Iconify(
                                  CuteIconifyIcons.eyeClosedCute,
                                  key: const ValueKey<bool>(false),
                                  color: _isFocused ? AppColors.darkSlate : AppColors.textMuted,
                                  size: 20,
                                ),
                        ),
                        onPressed: () {
                          setState(() {
                            _obscureText = !_obscureText;
                          });
                        },
                      ),
                    )
                  : null,
              suffixIconConstraints: const BoxConstraints(
                minWidth: 48,
                minHeight: 48,
              ),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 20,
                vertical: 16,
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(AppRadius.pill),
                borderSide: BorderSide.none,
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(AppRadius.pill),
                borderSide: const BorderSide(
                  color: Color(0xFFE5EBE0),
                  width: 1.2,
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(AppRadius.pill),
                borderSide: BorderSide(
                  color: widget.activeColor,
                  width: 2.0,
                ),
              ),
              errorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(AppRadius.pill),
                borderSide: const BorderSide(
                  color: AppColors.heartRed,
                  width: 1.5,
                ),
              ),
              focusedErrorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(AppRadius.pill),
                borderSide: const BorderSide(
                  color: AppColors.heartRed,
                  width: 2.0,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
