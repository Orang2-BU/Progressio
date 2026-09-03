import 'package:flutter/material.dart';
import 'package:iconify_flutter/iconify_flutter.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_spacing.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';
import 'package:progressio_mobile/core/constants/cute_iconify_icons.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// AnimatedDopamineTextField — Floating Label cut-out border pill
/// Label melayang mulus ke atas memotong border saat fokus atau terisi teks.
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
    this.activeColor = AppColors.lavenderPrimary,
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
    widget.controller.addListener(() {
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bool hasText = widget.controller.text.isNotEmpty;
    final bool isFloated = _isFocused || hasText;

    return Theme(
      data: Theme.of(context).copyWith(
        colorScheme: Theme.of(context).colorScheme.copyWith(
          primary: widget.activeColor,
        ),
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
          labelText: widget.label,
          labelStyle: TextStyle(
            fontFamily: AppTypography.headlineFont,
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: _isFocused ? widget.activeColor : AppColors.textMuted,
          ),
          floatingLabelStyle: TextStyle(
            fontFamily: AppTypography.headlineFont,
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: _isFocused ? widget.activeColor : AppColors.textMuted,
          ),
          floatingLabelBehavior: FloatingLabelBehavior.auto,
          hintText: isFloated ? widget.hintText : null,
          hintStyle: const TextStyle(
            color: AppColors.textMuted,
            fontSize: 13,
          ),
          filled: true,
          fillColor: Colors.white,
          prefixIcon: Padding(
            padding: const EdgeInsets.only(left: 18, right: 12),
            child: widget.iconifySvg != null
                ? Iconify(
                    widget.iconifySvg!,
                    color: _isFocused ? widget.activeColor : (hasText ? AppColors.textMain : AppColors.textMuted),
                    size: 21,
                  )
                : Icon(
                    widget.prefixIcon ?? Icons.star,
                    color: _isFocused ? widget.activeColor : (hasText ? AppColors.textMain : AppColors.textMuted),
                    size: 20,
                  ),
          ),
          prefixIconConstraints: const BoxConstraints(
            minWidth: 52,
            minHeight: 24,
          ),
          suffixIcon: widget.isPassword
              ? Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: IconButton(
                    iconSize: 22,
                    splashRadius: 20,
                    constraints: const BoxConstraints(
                      minWidth: 40,
                      minHeight: 40,
                    ),
                    icon: Iconify(
                      _obscureText ? CuteIconifyIcons.eyeCute : CuteIconifyIcons.eyeClosedCute,
                      color: _isFocused ? widget.activeColor : AppColors.textMuted,
                      size: 20,
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
            horizontal: 22,
            vertical: 18,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppRadius.pill),
            borderSide: const BorderSide(
              color: Color(0xFFE2E8DE),
              width: 1.5,
            ),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppRadius.pill),
            borderSide: const BorderSide(
              color: Color(0xFFE2E8DE),
              width: 1.5,
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
    );
  }
}
