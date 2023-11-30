/*Daily - BOM - CoSo*/

/*Actual vs Target - New Accounts (Tài khoản mở mới - Thực tế và chỉ tiêu) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @WorkDaysOfYear INT;
SET @WorkDaysOfYear = (
	SELECT COUNT(*) 
	FROM [Date] 
	WHERE [Work] = 1 
		AND YEAR([Date]) = YEAR(@Date)
);

WITH

[TargetByBranch] AS (
	SELECT 
        [BranchID] 
        , CAST(CAST([Target] AS FLOAT) / @WorkDaysOfYear AS DECIMAL(30,8)) [NewAccounts]
    FROM [DWH-AppData].[dbo].[BMD.FlexTarget]
    WHERE [Year] = YEAR(@Date)
        AND [Measure] = 'New Accounts'
)

, [RRE0386.Flex] AS (
	SELECT
		[AUTOID]
		, MIN([AUTOID]) OVER (PARTITION BY [SoTaiKhoan], [NgayMoTK]) [MinID]
		, [NgayMoTK]
		, [SoTaiKhoan]
		, [IDNhanVienMoTK]
	FROM [RRE0386]
	WHERE [RRE0386].[NgayMoTK] = @Date
		AND [RRE0386].[IDNhanVienHienTai] IS NOT NULL
)

, [FindLastBranchID] AS (
	SELECT DISTINCT
		[relationship].[date]
		, [relationship].[account_code] [SoTaiKhoan]
		, [broker_id]
		, LAST_VALUE([branch_id]) OVER(PARTITION BY [account_code], [broker_id] ORDER BY [account_code]) [branch_id]
	FROM [relationship]
	WHERE [relationship].[date] = @Date
		AND [relationship].[account_code] IN (SELECT [SoTaiKhoan] FROM [RRE0386.Flex])
)

, [Rel] AS (
	SELECT
		[Date]
		, [SoTaiKhoan]
		, CASE
			WHEN [broker_id] IS NULL AND [date] <> @Date THEN LEAD([branch_id]) OVER (PARTITION BY [SoTaiKhoan] ORDER BY [date])
			ELSE [branch_id]
		END [BranchID]
	FROM [FindLastBranchID]
)

, [_RRE0386] AS (
	SELECT
		[NgayMoTK]
		, [SoTaiKhoan]
		, [IDNhanVienMoTK]
	FROM [RRE0386.Flex]
	WHERE [MinID] = [AUTOID]
)

, [BranchActual] AS (
	SELECT
		[Rel].[BranchID]
		, CAST(COUNT(*) AS DECIMAL(20,2)) [NewAccounts]
	FROM [_RRE0386]
	LEFT JOIN [Rel]
		ON [Rel].[SoTaiKhoan] = [_RRE0386].[SoTaiKhoan]
		AND [Rel].[Date] = [_RRE0386].[NgayMoTK]
	GROUP BY [Rel].[BranchID]
)

SELECT
	[TargetByBranch].[BranchID]
	, ISNULL([BranchActual].[NewAccounts],0) [Actual]
    , [TargetByBranch].[NewAccounts] [Target]
FROM [TargetByBranch]
LEFT JOIN [BranchActual]
    ON [TargetByBranch].[BranchID] = [BranchActual].[BranchID]
ORDER BY 1


END