/*Daily - BOM - CoSo*/

/*Headline Tag - New Accounts (Phần trăm hoàn thành chỉ tiêu ngày - Tài khoản mở mới) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Prev DATETIME;
SET @Prev = (
	SELECT MIN([Date]) 
	FROM (
		SELECT TOP 2
			[Date]
		FROM [Date]
		WHERE [Work] = 1
			AND [Date] <= @Date
		ORDER BY [Date] DESC
	) [z]
);

WITH

[TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
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
	WHERE [RRE0386].[NgayMoTK] IN (@Prev, @Date)
		AND [RRE0386].[IDNhanVienHienTai] IS NOT NULL
)

, [FindLastBranchID] AS (
	SELECT DISTINCT
		[relationship].[date]
		, [relationship].[account_code] [SoTaiKhoan]
		, [broker_id]
		, LAST_VALUE([branch_id]) OVER(PARTITION BY [account_code], [broker_id] ORDER BY [account_code]) [branch_id]
	FROM [relationship]
	WHERE [relationship].[date] IN (@Prev, @Date)
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

, [PrevValue] AS (
	SELECT
		COUNT(*) [NewAccounts]
	FROM [_RRE0386]
	LEFT JOIN [Rel]
		ON [Rel].[SoTaiKhoan] = [_RRE0386].[SoTaiKhoan]
		AND [Rel].[Date] = [_RRE0386].[NgayMoTK]
	WHERE [Rel].[BranchID] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [_RRE0386].[NgayMoTK] = @Prev
)

, [TodayValue] AS (
	SELECT
		COUNT(*) [NewAccounts]
	FROM [_RRE0386]
	LEFT JOIN [Rel]
		ON [Rel].[SoTaiKhoan] = [_RRE0386].[SoTaiKhoan]
		AND [Rel].[Date] = [_RRE0386].[NgayMoTK]
	WHERE [Rel].[BranchID] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [_RRE0386].[NgayMoTK] = @Date
)

SELECT
	[TodayValue].[NewAccounts] [NewAccounts]
	, CAST([TodayValue].[NewAccounts] AS DECIMAL(10,5)) - CAST([PrevValue].[NewAccounts] AS DECIMAL(10,5)) [AbsoluteChange]
	, CASE [PrevValue].[NewAccounts]
		WHEN 0 THEN 0
		ELSE CAST([TodayValue].[NewAccounts] AS DECIMAL(10,5)) / CAST([PrevValue].[NewAccounts] AS DECIMAL(10,5)) - 1
	END [RelativeChange]
FROM [PrevValue]
CROSS JOIN [TodayValue]


END
