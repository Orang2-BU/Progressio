import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:progressio_mobile/app/app.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  // Status bar: dark icons on light background
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      statusBarBrightness: Brightness.light,
    ),
  );

  runApp(const ProgressioApp());
}
